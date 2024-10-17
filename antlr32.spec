%{?_javapackages_macros:%_javapackages_macros}
%global bootstrap 1
%global bootstrap_version 3.1.3

Name:           antlr32
Version:        3.2
Release:        5.3
Summary:        ANother Tool for Language Recognition
Group:		Development/Java
License:        BSD
URL:            https://www.antlr3.org/
Source0:        http://www.antlr3.org/download/antlr-%{version}.tar.gz

# These artifacts are taken verbatim from maven central with the exception of the
# jar in source 2, which additionally has the java 8 compatibility patch given below
# These sources are only used for bootstrapping antlr32 into a new distro
%if %{bootstrap}
Source1:        http://repo1.maven.org/maven2/org/antlr/antlr-master/%{bootstrap_version}/antlr-master-%{bootstrap_version}.pom
Source2:        http://repo1.maven.org/maven2/org/antlr/antlr/%{bootstrap_version}/antlr-%{bootstrap_version}.jar
Source3:        http://repo1.maven.org/maven2/org/antlr/antlr/%{bootstrap_version}/antlr-%{bootstrap_version}.pom
Source4:        http://repo1.maven.org/maven2/org/antlr/antlr-runtime/%{bootstrap_version}/antlr-runtime-%{bootstrap_version}.jar
Source5:        http://repo1.maven.org/maven2/org/antlr/antlr-runtime/%{bootstrap_version}/antlr-runtime-%{bootstrap_version}.pom
Source6:        http://repo1.maven.org/maven2/org/antlr/antlr3-maven-plugin/%{bootstrap_version}-1/antlr3-maven-plugin-%{bootstrap_version}-1.jar
Source7:        http://repo1.maven.org/maven2/org/antlr/antlr3-maven-plugin/%{bootstrap_version}-1/antlr3-maven-plugin-%{bootstrap_version}-1.pom
%endif

# This is backported from upstream antlr 3.5.2 for java 8 compatibility
# See https://github.com/antlr/antlr3/commit/e88907c259c43d42fa5e9f5ad0e486a2c1e004bb
Patch0:         java8-compat.patch

BuildRequires:  maven-local
BuildRequires:  antlr-maven-plugin
BuildRequires:  stringtemplate >= 3.2

# Cannot require ourself when bootstrapping
%if ! %{bootstrap}
BuildRequires:  %{name}-maven-plugin = %{version}
%endif

BuildArch:      noarch

%description
ANother Tool for Language Recognition, is a grammar parser generator.
This package is compatibility package containing an older version of
in order to support jython. No other packages should declare a
dependency on this one.

%package     maven-plugin
Summary:     Maven plug-in for creating ANTLR-generated parsers
Requires:    %{name}-tool = %{version}-%{release}

%description maven-plugin
Maven plug-in for creating ANTLR-generated parsers.

%package     tool
Summary:     Command line tool for creating ANTLR-generated parsers
Requires:    %{name}-java = %{version}-%{release}

%description tool
Command line tool for creating ANTLR-generated parsers.

%package     java
Summary:     Java run-time support for ANTLR-generated parsers
Requires:    stringtemplate >= 3.2

%description java
Java run-time support for ANTLR-generated parsers.

%package     javadoc
Summary:     API documentation for ANTLR

%description javadoc
%{summary}.

%prep
%setup -q -n antlr-%{version}

%patch0 -p0 -b .orig

# remove pre-built artifacts
find -type f -a -name *.jar -delete
find -type f -a -name *.class -delete

# remove corrupted files
find -name "._*" -delete

# disable stuff we don't need
%pom_disable_module gunit
%pom_disable_module gunit-maven-plugin
%pom_remove_plugin org.codehaus.mojo:buildnumber-maven-plugin
%pom_xpath_remove pom:build/pom:extensions
%pom_xpath_remove pom:build/pom:extensions runtime/Java
%pom_xpath_remove pom:build/pom:extensions antlr3-maven-plugin

# separate artifacts into sub-packages
%mvn_package :antlr tool
%mvn_package :antlr-master java
%mvn_package :antlr-runtime java
%mvn_package :antlr3-maven-plugin maven-plugin

# use a valid build target
find -name "pom.xml" | xargs sed -i -e "s|>jsr14<|>1.5<|"

# set a build number
sed -i -e "s|\${buildNumber}|%{release}|" tool/src/main/resources/org/antlr/antlr.properties

%mvn_compat_version org.antlr: %{bootstrap_version} 3.2

%build
mkdir -p .m2/org/antlr/antlr-master/%{version}/
cp -p pom.xml .m2/org/antlr/antlr-master/%{version}/antlr-master-%{version}.pom

%if %{bootstrap}
mkdir -p .m2/org/antlr/antlr-master/%{bootstrap_version}/
cp -p %{SOURCE1} .m2/org/antlr/antlr-master/%{bootstrap_version}/.
mkdir -p .m2/org/antlr/antlr/%{bootstrap_version}/
cp -p %{SOURCE2} %{SOURCE3} .m2/org/antlr/antlr/%{bootstrap_version}/.
mkdir -p .m2/org/antlr/antlr-runtime/%{bootstrap_version}/
cp -p %{SOURCE4} %{SOURCE5} .m2/org/antlr/antlr-runtime/%{bootstrap_version}/.
mkdir -p .m2/org/antlr/antlr3-maven-plugin/%{bootstrap_version}-1/
cp -p %{SOURCE6} %{SOURCE7} .m2/org/antlr/antlr3-maven-plugin/%{bootstrap_version}-1/.
%endif

# a small number of tests always fail for reasons I don't fully understand
%mvn_build -f

%install
%mvn_install

%files tool -f .mfiles-tool
%doc tool/LICENSE.txt

%files maven-plugin -f .mfiles-maven-plugin
%doc tool/LICENSE.txt

%files java -f .mfiles-java
%doc tool/LICENSE.txt
%dir %{_datadir}/java/%{name}

%files javadoc -f .mfiles-javadoc
%doc tool/LICENSE.txt

%changelog
* Fri Jun 20 2014 Mat Booth <mat.booth@redhat.com> - 3.2-5
- Use mvn_compat_version macro

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Jun 02 2014 Mat Booth <mat.booth@redhat.com> - 3.2-3
- Perform a non-bootstrap build

* Mon Jun 02 2014 Mat Booth <mat.booth@redhat.com> - 3.2-2
- Add link to source of back-ported patch

* Thu May 29 2014 Mat Booth <mat.booth@redhat.com> - 3.2-1
- Initial packaging of compatability version of antlr3

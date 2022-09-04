%bcond_without autoconf
Summary:             Gives a fake root environment
Name:                fakeroot
Version:             1.29
Release:             1
License:             GPLv3+ and LGPLv2.1 and MIT and GPL+ 
URL:                 https://tracker.debian.org/pkg/fakeroot
Source0:             https://salsa.debian.org/clint/fakeroot/-/archive/upstream/%{version}/%{name}-upstream-%{version}.tar.bz2
%if %{with autoconf}
BuildRequires:       autoconf automake libtool po4a
%endif
BuildRequires:       /usr/bin/getopt  libacl-devel libcap-devel sharutils
Requires:            /usr/bin/getopt fakeroot-libs = %{version}-%{release}
Requires(post):      /usr/sbin/alternatives
Requires(post):      /usr/bin/readlink
Requires(preun):     /usr/sbin/alternatives
%description
fakeroot runs a command in an environment wherein it appears to have
root privileges for file manipulation. fakeroot works by replacing the
file manipulation library functions (chmod(2), stat(2) etc.) by ones
that simulate the effect the real library functions would have had,
had the user really been root.

%package libs
Summary:             Gives a fake root environment (libraries)
%description libs
This package contains the libraries required by %{name}.

%prep
%autosetup -p1 -n   %{name}-upstream-%{version}

%build
%if %{with autoconf}
./bootstrap
pushd doc
po4a -k 0 --rm-backups --variable "srcdir=../doc/" po4a/po4a.cfg
popd
%endif
for file in ./doc/{*.1,*/*.1}; do
  iconv -f latin1 -t utf8 < $file > $file.new && \
  mv -f $file.new $file
done
for type in sysv tcp; do
mkdir obj-$type
cd obj-$type
cat >> configure << 'EOF'
exec ../configure "$@"
EOF
chmod +x configure
%configure \
  --disable-dependency-tracking \
  --disable-static \
  --libdir=%{_libdir}/libfakeroot \
  --with-ipc=$type \
  --program-suffix=-$type
make
cd ..
done

%install
for type in sysv tcp; do
  make -C obj-$type install libdir=%{_libdir}/libfakeroot DESTDIR=%{buildroot}
  mv %{buildroot}%{_libdir}/libfakeroot/libfakeroot-0.so \
     %{buildroot}%{_libdir}/libfakeroot/libfakeroot-$type.so
  rm -f %{buildroot}%{_libdir}/libfakeroot/libfakeroot.so
  rm -f %{buildroot}%{_libdir}/libfakeroot/libfakeroot.*la
  %find_lang faked-$type --without-mo --with-man
  %find_lang fakeroot-$type --without-mo --with-man
done
rm %{buildroot}%{_mandir}{,/*}/man1/fake{d,root}-sysv.1
rename -- -tcp '' %{buildroot}%{_mandir}{,/*}/man1/fake{d,root}-tcp.1
sed -e 's/-tcp//g' fake{d,root}-tcp.lang > fakeroot.lang

%check
for type in sysv tcp; do
  make -C obj-$type check VERBOSE=1
done

%post
link=$(readlink -e "/usr/bin/fakeroot")
if [ "$link" = "/usr/bin/fakeroot" ]; then
  rm -f /usr/bin/fakeroot
fi
link=$(readlink -e "%{_bindir}/faked")
if [ "$link" = "%{_bindir}/faked" ]; then
  rm -f "%{_bindir}/faked"
fi
link=$(readlink -e "%{_libdir}/libfakeroot/libfakeroot-0.so")
if [ "$link" = "%{_libdir}/libfakeroot/libfakeroot-0.so" ]; then
  rm -f "%{_libdir}/libfakeroot/libfakeroot-0.so"
fi
/usr/sbin/alternatives --install "%{_bindir}/fakeroot" fakeroot \
  "%{_bindir}/fakeroot-tcp" 50 \
  --slave %{_bindir}/faked faked %{_bindir}/faked-tcp \
  --slave %{_libdir}/libfakeroot/libfakeroot-0.so libfakeroot.so %{_libdir}/libfakeroot/libfakeroot-tcp.so
/usr/sbin/alternatives --install "%{_bindir}/fakeroot" fakeroot \
  "%{_bindir}/fakeroot-sysv" 40 \
  --slave %{_bindir}/faked faked %{_bindir}/faked-sysv \
  --slave %{_libdir}/libfakeroot/libfakeroot-0.so libfakeroot.so %{_libdir}/libfakeroot/libfakeroot-sysv.so \

%preun
if [ $1 = 0 ]; then
  /usr/sbin/alternatives --remove fakeroot "%{_bindir}/fakeroot-tcp"
  /usr/sbin/alternatives --remove fakeroot "%{_bindir}/fakeroot-sysv"
fi

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc COPYING AUTHORS BUGS DEBUG doc/README.saving
%{_bindir}/faked-*
%ghost %{_bindir}/faked
%{_bindir}/fakeroot-*
%ghost %{_bindir}/fakeroot
%{_mandir}/man1/faked.1*
%{_mandir}/man1/fakeroot.1*

%files libs
%dir %{_libdir}/libfakeroot
%{_libdir}/libfakeroot/libfakeroot-sysv.so
%{_libdir}/libfakeroot/libfakeroot-tcp.so
%ghost %{_libdir}/libfakeroot/libfakeroot-0.so

%changelog
* Fri Jun 24 2022 wangyangdahai <admin@you2.top> - 1.29-1
- Update version 1.29

* Tue Jun 21 2022 liyanan <liyanan32@h-partners.com> - 1.25.2-3
- Skip tar test: the test is unstable and keeps on randomly failing

* Sat Mar 13 2021 shixuantong <shixuantong@huawei.com> - 1.25.2-2
- Fix error: '_STAT_VER' undeclared

* Fri Nov 20 2020 zhangjiapeng <zhangjiapeng9@huawei.com> - 1.25.2-1
- Update to 1.25.2

* Wed Aug 12 2020 zhangjiapeng <zhangjiapeng9@huawei.com> - 1.23-3
- remove four test cases to solve the compilation failure

* Fri Nov 29 2019 lihao <lihao129@huawei.com> - 1.23-2
- Package Init

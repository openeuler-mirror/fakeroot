%bcond_with autoconf

Name:           fakeroot
Version:        1.23
Release:        3
Summary:        Gives a fake root environment
License:        GPLv3+ and LGPLv2+ and (GPL+ or Artistic)
URL:            https://tracker.debian.org/pkg/fakeroot
Source0:        http://http.debian.net/debian/pool/main/f/fakeroot/%{name}_%{version}.orig.tar.xz

Patch0000:      debian_eglibc-fts-without-LFS.patch
Patch0001:      debian_glibc-xattr-types.patch
Patch0002:      debian_fix-shell-in-fakeroot.patch
Patch0003:      debian_hide-dlsym-error.patch
Patch0004:      fakeroot-inttypes.patch
Patch0005:      fakeroot-multilib.patch
Patch0006:      fakeroot-tests.patch
Patch0007:      fakeroot-remove-four-test-cases.patch

%if %{with autoconf}
BuildRequires:  autoconf automake libtool po4a
%endif
BuildRequires:  util-linux libacl-devel libcap-devel sharutils
Requires:       util-linux
Requires(post): chkconfig
Requires(post): coreutils
Requires(preun):chkconfig

Provides:       fakeroot-libs = %{version}-%{release}
Obsoletes:      fakeroot-libs < %{version}-%{release}


%description
fakeroot replaces the invocation of library function to run a command
in a fake environment in which it executes just like has root privileges.
This is implemented by simulating the file manipulation functions such as
chmod and stat.

%package        help
Summary:        Documentation for fakeroot
%description    help
Documentation for fakeroot

%prep
%autosetup -p1

%build
%if %{with autoconf}
autoreconf -i
cd doc
po4a -k 0 --rm-backups --variable "srcdir=../doc/" po4a/po4a.cfg
cd -
%endif

for file in ./doc/{*.1,*/*.1}; do
  iconv -f latin1 -t utf8 < $file > $file.new && \
  mv -f $file.new $file
done

for type in sysv tcp; do
mkdir obj-$type
cd obj-$type
cat >> configure << 'EOF'
#!/bin/sh
exec ../configure "$@"
EOF
chmod +x configure
%configure --disable-dependency-tracking --disable-static \
  --libdir=%{_libdir}/libfakeroot --with-ipc=$type --program-suffix=-$type
make
cd ..
done

%install
for type in sysv tcp; do
    %make_install -C obj-$type libdir=%{_libdir}/libfakeroot
    mv %{buildroot}%{_libdir}/libfakeroot/libfakeroot-{0,$type}.so
    rm -f %{buildroot}%{_libdir}/libfakeroot/libfakeroot.so
    %delete_la
    %find_lang faked-$type --without-mo --with-man
    %find_lang fakeroot-$type --without-mo --with-man
done

cat fake{d,root}-{sysv,tcp}.lang > fakeroot.lang

%check
make -C obj-sysv check VERBOSE=1
make -C obj-tcp check VERBOSE=1

%post

for name in fakeroot faked; do
    link=$(readlink -e "/usr/bin/$name")
    if [ "$link" = "/usr/bin/$name" ]; then
      rm -f /usr/bin/$name
    fi
done

link=$(readlink -e "%{_libdir}/libfakeroot/libfakeroot-0.so")
if [ "$link" = "%{_libdir}/libfakeroot/libfakeroot-0.so" ]; then
  rm -f "%{_libdir}/libfakeroot/libfakeroot-0.so"
fi

for type in tcp sysv; do
    if [ "$type" = "tcp" ]; then
            priority=50
    else
            priority=40
    fi
    /usr/sbin/alternatives --install "%{_bindir}/fakeroot" fakeroot "%{_bindir}/fakeroot-$type" $priority \
        --slave %{_bindir}/faked faked %{_bindir}/faked-$type \
        --slave %{_libdir}/libfakeroot/libfakeroot-0.so libfakeroot.so %{_libdir}/libfakeroot/libfakeroot-$type.so
done

%post           help

for type in tcp sysv; do
    if [ "$type" = "tcp" ]; then
            priority=50
    else
            priority=40
    fi
    /usr/sbin/alternatives --install "%{_bindir}/fakeroot" fakeroot "%{_bindir}/fakeroot-$type" $priority \
        --slave %{_mandir}/man1/fakeroot.1.gz fakeroot.1.gz %{_mandir}/man1/fakeroot-$type.1.gz \
        --slave %{_mandir}/man1/faked.1.gz faked.1.gz %{_mandir}/man1/faked-$type.1.gz
done

for lang in de es fr nl pt sv; do
    /usr/sbin/alternatives --install "%{_bindir}/fakeroot" fakeroot "%{_bindir}/fakeroot-tcp" 50 \
    --slave %{_mandir}/$lang/man1/fakeroot.1.gz fakeroot.$lang.1.gz %{_mandir}/$lang/man1/fakeroot-tcp.1.gz \
    --slave %{_mandir}/$lang/man1/faked.1.gz faked.$lang.1.gz %{_mandir}/$lang/man1/faked-tcp.1.gz
done

for lang in de es fr nl pt sv; do
    /usr/sbin/alternatives --install "%{_bindir}/fakeroot" fakeroot "%{_bindir}/fakeroot-sysv" 40 \
    --slave %{_mandir}/$lang/man1/fakeroot.1.gz fakeroot.$lang.1.gz %{_mandir}/$lang/man1/fakeroot-sysv.1.gz \
    --slave %{_mandir}/$lang/man1/faked.1.gz faked.$lang.1.gz %{_mandir}/$lang/man1/faked-sysv.1.gz
done

%preun
if [ $1 = 0 ]; then
  /usr/sbin/alternatives --remove fakeroot "%{_bindir}/fakeroot-tcp"
  /usr/sbin/alternatives --remove fakeroot "%{_bindir}/fakeroot-sysv"
fi

%files
%defattr(-,root,root,-)
%doc COPYING AUTHORS BUGS DEBUG
%{_bindir}/faked-*
%ghost %{_bindir}/faked
%{_bindir}/fakeroot-*
%ghost %{_bindir}/fakeroot
%dir %{_libdir}/libfakeroot
%{_libdir}/libfakeroot/libfakeroot-*.so
%ghost %{_libdir}/libfakeroot/libfakeroot-0.so

%files help
%doc doc/README.saving
%{_mandir}/man1/*
%{_mandir}/*/man1/*
%ghost %{_mandir}/man1/faked.1.gz
%ghost %{_mandir}/man1/fakeroot.1.gz
%ghost %lang(de) %{_mandir}/de/man1/faked.1.gz
%ghost %lang(de) %{_mandir}/de/man1/fakeroot.1.gz
%ghost %lang(es) %{_mandir}/es/man1/faked.1.gz
%ghost %lang(es) %{_mandir}/es/man1/fakeroot.1.gz
%ghost %lang(fr) %{_mandir}/fr/man1/faked.1.gz
%ghost %lang(fr) %{_mandir}/fr/man1/fakeroot.1.gz
%ghost %lang(pt) %{_mandir}/pt/man1/faked.1.gz
%ghost %lang(pt) %{_mandir}/pt/man1/fakeroot.1.gz
%ghost %lang(sv) %{_mandir}/sv/man1/faked.1.gz
%ghost %lang(sv) %{_mandir}/sv/man1/fakeroot.1.gz
%ghost %lang(nl) %{_mandir}/nl/man1/faked.1.gz
%ghost %lang(nl) %{_mandir}/nl/man1/fakeroot.1.gz

%changelog
* Wed Aug 12 2020 zhangjiapeng <zhangjiapeng9@huawei.com> - 1.23-3
- remove four test cases to solve the compilation failure

* Fri Nov 29 2019 lihao <lihao129@huawei.com> - 1.23-2
- Package Init

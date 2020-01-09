Name:           fcoe-utils
Version:        1.0.22
Release:        3%{?dist}
Summary:        Fibre Channel over Ethernet utilities
Group:          Applications/System
License:        GPLv2
URL:            http://www.open-fcoe.org
# Source is a git snapshot, git://open-fcoe.org/fcoe/fcoe-utils.git
Source0:        %{name}-%{version}.tar.bz2
Source1:        quickstart.txt
ExcludeArch:    s390 ppc
# General
Patch0:         fcoe-utils-1.0.22-init.patch
Patch1:         fcoe-utils-1.0.20-make.patch
Patch2:         fcoe-utils-1.0.18-help.patch
Patch3:         fcoe-utils-1.0.18-config.patch
# Upstream patches
Patch10:        fcoe-utils-1.0.22-debug-Add-date-and-ps-output-to-fcoedump.sh.patch

BuildRequires:      libtool automake autoconf
BuildRequires:      lldpad-devel >= 0.9.43
BuildRequires:      libhbaapi-devel >= 2.2-11
BuildRequires:      libhbalinux-devel >= 1.0.13
BuildRequires:      libnl-devel
Requires:           lldpad >= 0.9.43
Requires:           libhbalinux >= 1.0.13
Requires:           iproute
Requires:           device-mapper-multipath

Requires(post):   chkconfig
Requires(preun):  chkconfig initscripts
Requires(postun): initscripts

%description
Fibre Channel over Ethernet utilities
fcoeadm - command line tool for configuring FCoE interfaces
fcoemon - service to configure DCB Ethernet QOS filters, works with dcbd or
lldpad

%prep
%setup -q
# Upstream
%patch10 -p1
# RH-specific
%patch0 -p1 -b .init
%patch1 -p1 -b .make
%patch2 -p1 -b .help
%patch3 -p1 -b .config

%build
./bootstrap.sh
%configure
make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}
mkdir -p %{buildroot}%{_initrddir}
mv %{buildroot}/etc/init.d/fcoe %{buildroot}%{_initrddir}/fcoe
rm -rf %{buildroot}/etc/init.d
install -m 644 %SOURCE1 quickstart.txt
mkdir -p %{buildroot}%{_sysconfdir}/fcoe/
cp etc/config %{buildroot}%{_sysconfdir}/fcoe/config
mkdir -p %{buildroot}%{_libexecdir}/fcoe

install -m 755 contrib/fcc.sh %{buildroot}%{_libexecdir}/fcoe/fcc.sh
install -m 755 contrib/fcoe_edd.sh %{buildroot}%{_libexecdir}/fcoe/fcoe_edd.sh
install -m 755 contrib/fcoe-setup.sh %{buildroot}%{_libexecdir}/fcoe/fcoe-setup.sh
install -m 755 debug/fcoedump.sh %{buildroot}%{_libexecdir}/fcoe/fcoedump.sh
install -m 755 debug/dcbcheck.sh %{buildroot}%{_libexecdir}/fcoe/dcbcheck.sh

%post
/sbin/chkconfig --add fcoe

%triggerun -- fcoe-utils <= 1.0.7-5
if [ -x %{_initrddir}/fcoe-utils ]; then
  /sbin/service fcoe-utils stop > /dev/null 2>&1
  /sbin/chkconfig fcoe-utils off
  # now copy an updated file, which we need to do proper condrestart
  sed 's/\/var\/lock\/subsys\/fcoe/\/var\/lock\/subsys\/fcoe-utils/' %{_initrddir}/fcoe > %{_initrddir}/fcoe-utils
fi

%triggerpostun -- fcoe-utils <= 1.0.7-5
if [ -x %{_initrddir}/fcoe-utils ]; then
  rm -f %{_initrddir}/fcoe-utils # this file should be already deleted, but just in case ...
fi

%preun
if [ $1 = 0 ]; then
        /sbin/service fcoe stop > /dev/null 2>&1
        /sbin/chkconfig --del fcoe
fi

%postun
if [ "$1" -ge "1" ]; then
        /sbin/service fcoe condrestart > /dev/null  2>&1 || :
fi


%files
%defattr(-,root,root,-)
%doc README COPYING quickstart.txt
%{_sbindir}/*
%{_mandir}/man8/*
%dir %{_sysconfdir}/fcoe/
%config(noreplace) %{_sysconfdir}/fcoe/config
%config(noreplace) %{_sysconfdir}/fcoe/cfg-ethx
%dir %{_sysconfdir}/bash_completion.d/
%{_sysconfdir}/bash_completion.d/*
%{_initrddir}/fcoe
%attr(0755,root,root) %{_libexecdir}/fcoe/fcoe_edd.sh
%attr(0755,root,root) %{_libexecdir}/fcoe/fcoe-setup.sh
%attr(0755,root,root) %{_libexecdir}/fcoe/fcc.sh
%attr(0755,root,root) %{_libexecdir}/fcoe/fcoedump.sh
%attr(0755,root,root) %{_libexecdir}/fcoe/dcbcheck.sh


%changelog
* Mon Apr 02 2012 Petr Šabata <contyk@redhat.com> - 1.0.22-3
- Completely revert upstream initscript status() changes (#804936)

* Thu Mar 22 2012 Petr Šabata <contyk@redhat.com> - 1.0.22-2
- Reverting a part of d789267 upstream patch.  Initscript shouldn't return code 2 on
  status query when the daemon is running. (#804936)

* Thu Feb 16 2012 Petr Šabata <contyk@redhat.com> - 1.0.22-1
- Update to 1.0.22 with 7d3c9d1, "Add date and ps output to fcoedump.sh"
- Require libhbalinux-1.0.13 or newer

* Wed Nov 02 2011 Petr Sabata <contyk@redhat.com> - 1.0.20-5
- Also destroy FCoE interfaces created by fipvlan
- Resolves: rhbz#639466

* Mon Oct 10 2011 Petr Sabata <contyk@redhat.com> - 1.0.20-4
- Increase clif timeout to a reasonably large value (9f97f76)
- Resolves: rhbz#743689

* Fri Sep 16 2011 Petr Sabata <contyk@redhat.com> - 1.0.20-3
- Sync with upstream tip
- Resolves: rhbz#695941
- Resolves: rhbz#732485

* Thu Aug 11 2011 Petr Sabata <contyk@redhat.com> - 1.0.20-2
- Unload drivers on force stop
- Resolves: rhbz#639466

* Thu Jul 14 2011 Petr Sabata <contyk@redhat.com> - 1.0.20-1
- Update to 1.0.20
- Resolves: rhbz#695941

* Tue May  3 2011 Petr Sabata <psabata@redhat.com> - 1.0.18-2
- Don't create a world writable PID file
- Resolves: rhbz#700951

* Mon Apr 11 2011 Petr Sabata <psabata@redhat.com> - 1.0.18-1
- Sync with upstream up to commit 6394a804ef09b83b78348c189dc4b99b440e0f6b
- Resolves: rhbz#691613

* Wed Mar 23 2011 Petr Sabata <psabata@redhat.com> - 1.0.17-7
- Retry vlan discovery forever
- Resolves: rhbz#689631

* Wed Mar  2 2011 Petr Sabata <psabata@redhat.com> - 1.0.17-6
- Auto enable FCoE interface after ifup-ifdown
- Resolves: rhbz#680578

* Mon Feb 28 2011 Petr Sabata <psabata@redhat.com> - 1.0.17-5
- Do not assume version 0.1 for FCoE modules
- Related: rhbz#669211

* Fri Feb 18 2011 Petr Sabata <psabata@redhat.com> - 1.0.17-4
- Double free fix
- Resolves: rhbz#678487

* Mon Feb 14 2011 Petr Sabata <psabata@redhat.com> - 1.0.17-3
- Adding SUPPORTED_DRIVERS field, Patch12
- Related: rhbz#669211

* Tue Feb  8 2011 Petr Sabata <psabata@redhat.com> - 1.0.17-2
- Changing fcoemon.c includes temporarily to address open-lldp header changes
- Related: rhbz#672453

* Fri Feb  4 2011 Petr Sabata <psabata@redhat.com> - 1.0.17-1
- Rebase to 1.0.17
- Resolves: rhbz#672453

* Thu Feb  3 2011 Petr Sabata <psabata@redhat.com> - 1.0.14-18
- sysfs-libfcoe.patch -- changed SYSFS_FCOE macro to /sys/libfcoe/
- Resolves: rhbz#669211

* Tue Feb  1 2011 Petr Sabata <psabata@redhat.com> - 1.0.14-17
- netdev-wait.patch -- POSIX compliance fix; based on suggestion from Petr Pisar
- Related: rhbz#658076

* Tue Feb  1 2011 Petr Sabata <psabata@redhat.com> - 1.0.14-16
- remove-vconfig-dep.patch, contrib/fcoe-setup.sh
- removed vconfig requirement
- Resolves: rhbz#645796

* Tue Feb  1 2011 Petr Sabata <psabata@redhat.com> - 1.0.14-15
- netdev-wait.patch -- new config option, init script change
- Resolves: rhbz#658076

* Tue Jan 25 2011 Petr Sabata <psabata@redhat.com> - 1.0.14-14
- fcoeadm-scan.patch update, s/fcoe/FCoE/g;
- Related: rhbz#623567

* Mon Jan 24 2011 Petr Sabata <psabata@redhat.com> - 1.0.14-13
- fcoeadm-scan.patch
- Resolves: rhbz#623567

* Fri Jan 14 2011 Petr Sabata <psabata@redhat.com> - 1.0.14-12
- fcoemon-auto_vlan.patch
- Resolves: rhbz#619157

* Wed Jan  5 2011 Petr Sabata <psabata@redhat.com> - 1.0.14-11
- dont-hang-on-reboot.patch
- Resolves: rhbz#645917

* Thu Nov 18 2010 Petr Sabata <psabata@redhat.com> - 1.0.14-10
- fcnsq-usage.patch
- Related: rhbz#623567

* Wed Aug 18 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-9
- fixed fipvlan hangup during boot (#624786)

* Fri Jul 30 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-8
- fcoe service starts on all init levels - second try (#619604)

* Fri Jul 30 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-7
- critical bugfix on fipvlan (#618443)
- fcoe service starts on all init levels (#619604)

* Tue Jul 20 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-6
- some upstream fixes marked as critical (#615416)

* Tue Jul 13 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-5
- fixed init script - condrestart contained a small bug (#599499)

* Tue Jun 22 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-4
- added device-mapper-multipath to requires (#603242)
- added missing man pages (#594173)

* Thu Jun 03 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-3
- yet another update of init script - added condrestart and try-restart options

* Tue May 25 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-2
- updated init script to support force-reload option
  (alias to "restart force" as packaging guidelines suggest)

* Mon May 24 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.14-1
- rebased to 1.0.14 (see bug #593824 for a list of changes)

* Thu May 06 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.13-2
- added vconfig to requires (#589608)

* Mon Apr 12 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.13-1
- rebased to v1.0.13, some bugfixes, new FCoE related scripts

* Mon Mar 29 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.12-3.20100323git
- changed the name of sysfs_edd.sh to fcoe_edd.sh

* Tue Mar 23 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.12-2.20100323git
- some upstream updates:
- better fipvlan support (#571722)
- added sysfs_edd.sh script (#513018)

* Mon Mar 15 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.12-1
- rebased to version 1.0.12, improved functionality with lldpad
  and dcbd

* Fri Jan 15 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.10-2
- updated quickstart guide

* Wed Jan 13 2010 Jan Zeleny <jzeleny@redhat.com> - 1.0.10-1
- rebased to official 1.0.10 release

* Thu Dec 10 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.9-2.20091204git
- excluded s390 and ppc

* Fri Dec 04 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.9-1.20091204git
- rebase to latest version of fcoe-utils

* Mon Sep 14 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.8-3
- update of init script to be LSB-compliant

* Fri Jul 31 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.8-2
- patch for clean compilation without usage of upstream's ugly hack

* Thu Jul 30 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.8-1
- rebase of fcoe-utils to 1.0.8, adjusted spec file

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.7-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jun 9 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.7-7
- added quickstart file to doc (#500759)

* Thu May 14 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.7-6
- renamed init script to fcoe, changed lock filename to fcoe
  (#497604)
- init script modified to do condrestart properly
- some modifications in spec file to apply previous change
  to older versions od init script during update
- fixed issue with accepting long options (#498551)

* Mon May 4 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.7-5
- fixed SIGSEGV when fcoe module isn't loaded (#498550)

* Wed Apr 27 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.7-4
- added libhbalinux to Requires (#497605)
- correction of spec file (_initddir -> _initrddir)

* Wed Apr 8 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.7-3
- more minor corrections in spec file

* Thu Apr 2 2009 Jan Zeleny <jzeleny@redhat.com> - 1.0.7-2
- minor corrections in spec file
- moved init script to correct location
- correction in the init script (chkconfig directives)

* Mon Mar 2 2009 Chris Leech <christopher.leech@intel.com> - 1.0.7-1
- initial rpm build of fcoe tools


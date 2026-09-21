Name:           huiontablet
Version:        15.0.0.175
Release:        2%{?dist}
Summary:        Huion Tablet Driver
License:        Proprietary
URL:            https://www.huion.com/

# The Huion driver is proprietary and is NOT redistributed with this spec.
# Download the official Linux driver package (.deb) from Huion's download
# centre and place it in ~/rpmbuild/SOURCES/ under the name below:
#   https://www.huion.com/index.php?m=content&c=index&a=manual&id=742
Source0:        HuionTablet_LinuxDriver_v%{version}.x86_64.deb

BuildArch:      x86_64

BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  xz

Requires(pre):  shadow-utils
Requires:       libX11
Requires:       libXext
Requires:       libXi
Requires:       libXrender
Requires:       libxcb
Requires:       libxkbcommon
Requires:       libxkbcommon-x11
Requires:       libusb1

# Prebuilt vendor binaries, so there is nothing to produce debug symbols from.
%global debug_package %{nil}

# Huion's binaries carry a relative runpath "./libs" pointing at their bundled
# Qt, plus a stale absolute path from the vendor's own build machine. Fedora's
# check-rpaths rejects both. Rewriting the runpath in a proprietary binary risks
# breaking it, so the check is disabled here instead.
%global __brp_check_rpaths %{nil}

# The package bundles its own Qt 5 and Huion libraries under /usr/lib/huiontablet.
# Keep those out of the RPM dependency graph, so the bundled copies never satisfy
# another package's dependency and the bundled requires never leak out.
%global __provides_exclude_from ^/usr/lib/huiontablet/.*$
%global __requires_exclude_from ^/usr/lib/huiontablet/(libs|plugins|qml|xdotool)/.*$
%global __requires_exclude ^(libQt5|libQtSessionLib|libTabletSession|libcfgio|libhnusb|libhuionhid|libxdo|libicu|libpcre)

%description
Huion Tablet Driver and configuration software.

This Fedora package is rebuilt from the official Huion Linux driver
data files. The original Debian installation scripts are not included.

The driver writes per-device settings back into its own installation
directory, which fails on Fedora because /usr is root owned. This package
creates a "huion" system group and grants it write access to the driver's
configuration directory, so pen and express key mappings survive a restart
without running the driver as root.

%prep
rm -rf %{_builddir}/%{name}-%{version}
mkdir -p %{_builddir}/%{name}-%{version}
cd %{_builddir}/%{name}-%{version}
ar x %{SOURCE0}
tar -xf data.tar.*
rm -f data.tar.* control.tar.* debian-binary

%build
# Prebuilt Huion binaries. Nothing to compile.

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
cd %{_builddir}/%{name}-%{version}
cp -a usr %{buildroot}/
cp -a etc %{buildroot}/
rm -f %{buildroot}/usr/lib/huiontablet/.DriverUI.pid
rm -f %{buildroot}/usr/lib/huiontablet/.HuionCore.pid
rm -f %{buildroot}/usr/lib/huiontablet/.huion.log

%pre
getent group huion >/dev/null || groupadd -r huion
exit 0

%post
# huionCore and the Qt front end write per-device settings, a lock file and
# setting.ini into /usr/lib/huiontablet/res at runtime. Hand that directory
# to the huion group, with setgid so runtime files inherit the group.
chgrp -R huion /usr/lib/huiontablet || :
chmod 2775 /usr/lib/huiontablet /usr/lib/huiontablet/res || :
chmod 0664 /usr/lib/huiontablet/custom.conf /usr/lib/huiontablet/log.conf || :
chmod 0664 /usr/lib/huiontablet/res/*.cfg || :
chmod 0664 /usr/lib/huiontablet/res/.cfg || :
udevadm control --reload-rules || :
udevadm trigger || :

%postun
if [ "$1" -eq 0 ]; then
    # Runtime files created by the driver are not tracked by rpm.
    rm -f /usr/lib/huiontablet/res/setting.ini || :
    rm -f /usr/lib/huiontablet/res/setting.ini.lock || :
    rm -f /usr/lib/huiontablet/res/HUION_*.cfg || :
    rmdir /usr/lib/huiontablet/res 2>/dev/null || :
    rmdir /usr/lib/huiontablet 2>/dev/null || :
    udevadm control --reload-rules || :
    udevadm trigger || :
fi

%files
%dir /usr/lib/huiontablet
/usr/lib/huiontablet/*
%dir /usr/share/applications
/usr/share/applications/huiontablet.desktop
%dir /usr/share/icons
/usr/share/icons/huiontablet.png
%dir /etc/xdg
%dir /etc/xdg/autostart
/etc/xdg/autostart/huiontablet.desktop
%dir /usr/lib/udev
%dir /usr/lib/udev/rules.d
/usr/lib/udev/rules.d/20-huion.rules

%changelog
* Mon Sep 21 2026 Kuzhalogi Murthy <kuzhalogi@users.noreply.github.com> - 15.0.0.175-2
- Create a huion system group and grant it write access to the driver
  configuration directory, so pen and express key mappings persist
- Build directly from the official Huion .deb rather than a repacked tarball
- Disable check-rpaths, since the vendor binaries carry a relative runpath
  and a stale path from Huion's own build machine
- Keep bundled Qt and Huion libraries out of the RPM dependency graph
- Remove runtime state files on uninstall
- Note: %post adjusts ownership after install, so "rpm -V huiontablet"
  reports group and mode differences on those paths by design

* Mon Sep 21 2026 Kuzhalogi Murthy <kuzhalogi@users.noreply.github.com> - 15.0.0.175-1
- Repackaged official Huion Linux driver data for Fedora
- Removed Debian installer scripts
- Preserved Huion udev rules
- Does not disable Wayland

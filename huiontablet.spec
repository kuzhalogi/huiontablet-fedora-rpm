Name:           huiontablet
Version:        15.0.0.175
Release:        1%{?dist}
Summary:        Huion Tablet Driver
License:        Proprietary
URL:            https://www.huion.com/
Source0:        huion-data.tar.gz
BuildArch:      x86_64
%global debug_package %{nil}
Requires:       libX11
Requires:       libXext
Requires:       libXi
Requires:       libXrender
Requires:       libxcb
Requires:       libxkbcommon
Requires:       libxkbcommon-x11

%description
Huion Tablet Driver and configuration software.

This Fedora package is rebuilt from the official Huion Linux driver
data files. The original Debian installation scripts are not included.

%prep
%setup -q -n data

%build
# Prebuilt Huion binaries. Nothing to compile.

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
cp -a . %{buildroot}/
rm -f %{buildroot}/usr/lib/huiontablet/.DriverUI.pid
rm -f %{buildroot}/usr/lib/huiontablet/.HuionCore.pid
rm -f %{buildroot}/usr/lib/huiontablet/.huion.log

%post
udevadm control --reload-rules || :
udevadm trigger || :

%postun
if [ "$1" -eq 0 ]; then
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
* Mon Sep 21 2026 Huion Fedora package - 15.0.0.175-1
- Repackaged official Huion Linux driver data for Fedora
- Removed Debian installer scripts
- Preserved Huion udev rules
- Does not disable Wayland

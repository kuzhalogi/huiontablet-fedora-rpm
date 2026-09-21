# huiontablet-fedora-rpm

An RPM spec that builds Huion's official Linux tablet driver for Fedora, with the
settings-persistence bug fixed.

Tested on Fedora 44 Workstation, GNOME 50 on Wayland, driver version 15.0.0.175,
on a Huion Inspiroy H640P (USB ID `256c:006d`, internal model `T173`).

**The driver itself is Huion's proprietary software and is not redistributed here.**
This repository contains only the spec file. You download the driver from Huion and
build the package yourself.

## Why this exists

Huion ships a Linux driver as a Debian package built around one assumption: the
application may write to its own installation directory. On Fedora that directory is
`/usr/lib/huiontablet`, owned by root, so the driver applies your pen button mappings
in the running session and silently loses them at every restart. No error appears
anywhere.

Tracing the process shows what it wants:

```
openat(AT_FDCWD, "/usr/lib/huiontablet/res/HUION_T173.cfg", O_WRONLY|O_CREAT|O_TRUNC, 0666)
openat(AT_FDCWD, "/usr/lib/huiontablet/res/setting.ini.lock", O_RDWR|O_CREAT|O_EXCL|O_CLOEXEC, 0666)
```

A per-device `.cfg` file and a `setting.ini`, both inside the install tree.

This package creates a `huion` system group, gives the group write access to
`/usr/lib/huiontablet/res`, and sets the setgid bit so files the driver creates at
runtime inherit the group. Members of the group keep their settings. Nothing runs as
root, and nothing under `/usr` becomes world-writable.

## Requirements

```
sudo dnf install rpm-build rpmdevtools binutils
```

## Build

1. Download the official Linux driver from
   [Huion's download centre](https://www.huion.com/index.php?m=content&c=index&a=manual&id=742).
   Pick the `.deb` package.

2. Put it in your sources directory under the name the spec expects:

```
rpmdev-setuptree
cp ~/Downloads/HuionTablet_LinuxDriver_v15.0.0.175.x86_64.deb ~/rpmbuild/SOURCES/
```

   If your download has a different filename, either rename the file or edit `Source0`
   in the spec to match.

3. Build:

```
rpmbuild -bb huiontablet.spec
```

   The package lands in `~/rpmbuild/RPMS/x86_64/`.

   To verify the build in a clean chroot, which catches missing dependencies:

```
sudo dnf install mock
rpmbuild -bs huiontablet.spec
mock -r fedora-44-x86_64 --rebuild ~/rpmbuild/SRPMS/huiontablet-15.0.0.175-2.fc44.src.rpm
```

## Install

```
sudo dnf install ~/rpmbuild/RPMS/x86_64/huiontablet-15.0.0.175-2.fc44.x86_64.rpm
sudo usermod -aG huion "$USER"
```

Log out and back in. Group membership applies at login, and the same login starts the
driver through its autostart entry.

## Verify

```
pgrep -a huion
lsusb | grep -i 256c
ls -lt /usr/lib/huiontablet/res/ | head -5
```

You should see `huionCore` and `huiontablet` running, your tablet enumerated, and a
`HUION_*.cfg` file with a recent timestamp once you change a setting.

Confirm persistence by changing a pen button mapping, restarting the driver, and
checking the mapping again:

```
pkill -f /usr/lib/huiontablet
/usr/lib/huiontablet/huiontablet.sh
```

## Notes on Wayland

The driver works on GNOME under Wayland. Worth knowing why.

`huionCore` creates virtual input devices through `/dev/uhid` and `/dev/uinput`, so pen
position, pressure and express keys arrive as kernel input devices. Wayland compositors
read those directly, and express keys reach native Wayland applications normally.

The configuration GUI is Qt 5 and ships only the `xcb` platform plugin, so the window
runs through XWayland. That affects the settings window, not your pen input.

The bundled `xdotool` under `/usr/lib/huiontablet/xdotool` handles window and application
actions, and those remain X11 only.

## Known behaviour

The daemon writes `.HuionCore.pid`, `.DriverUI.pid` and `.huion.log` into its working
directory. Started from the autostart entry, the working directory is your home, so
three hidden files appear there. Harmless, and left alone by this package.

`rpm -V huiontablet` reports group and mode differences under `/usr/lib/huiontablet`.
That is the `%post` script doing its job, not corruption.

Per-device config files are named after your hardware, `HUION_T173.cfg` for example, so
your filename will differ.

## Licence

The spec file and everything else in this repository are MIT licensed, see `LICENSE`.

The Huion driver is proprietary software belonging to Huion and is covered by their own
terms. This repository does not distribute it, and the `License:` tag inside the spec
reflects the packaged software rather than the spec.

## Contributing

Reports from other Fedora releases and other Huion hardware are welcome. Include your
Fedora version, your tablet's USB ID from `lsusb`, and whether settings persist after a
restart.

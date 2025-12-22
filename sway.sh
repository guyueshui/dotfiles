#!/bin/bash

# Copied from .xinitrc in i3 setup.

# Fix Gnome Apps Slow  Start due to failing services
# Add this when you include flatpak in your system
# (add by yychi 2020-04-01 22:48)
# dbus-update-activation-environment --systemd DBUS_SESSION_BUS_ADDRESS DISPLAY XAUTHORITY

# dunst service panic, add this at 2025-03-03
# see: https://github.com/dunst-project/dunst/issues/1095#issuecomment-1250040627
# systemctl --user import-environment DISPLAY

# Do not set GTK_IM_MODULE, see:
#   https://fcitx-im.org/wiki/Using_Fcitx_5_on_Wayland
# export GTK_IM_MODULE=fcitx
#
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx

# Load X resource database, for XWayland
# xrdb -load ~/.Xresources

# Start sway
exec sway -d 2> /tmp/sway.log

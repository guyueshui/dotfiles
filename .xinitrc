#
# This file is parsed by pam_env module
#
# Syntax: simple "KEY=VAL" pairs on separate lines
#

# Fix Gnome Apps Slow  Start due to failing services
# Add this when you include flatpak in your system
# (add by yychi 2020-04-01 22:48)
dbus-update-activation-environment --systemd DBUS_SESSION_BUS_ADDRESS DISPLAY XAUTHORITY

export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx

# Load X resource database
xrdb -load ~/.Xresources

# exec gnome-session
exec i3

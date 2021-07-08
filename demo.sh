#!/bin/bash
run_xdotool () {
    for key in "${keys[@]}"
    do
        xdotool key $key
        $sleep_small
    done
}

clear_all () {
    keys=( ctrl+a BackSpace )
    run_xdotool
}

if [ "$1" == "ulauncher" ]; then
    ulauncher
    cmd="question space"
    sleep_small="sleep 0.02"
    sleep_big="sleep 2"
elif [ "$1" == "albert" ]; then
    albert show
    cmd="question space"
    sleep_small="sleep 0.02"
    sleep_big="sleep 2"
else
    exit
fi
sleep 0.05
clear_all
wmctrl -a "Ulauncher - Application Launcher"
sleep 4.4

keys=( $cmd D o w n l o a d s )
run_xdotool
$sleep_big

keys=( BackSpace BackSpace BackSpace BackSpace BackSpace BackSpace BackSpace BackSpace BackSpace )
run_xdotool
keys=( M u s i )
run_xdotool
$sleep_big

keys=( BackSpace BackSpace BackSpace BackSpace )
run_xdotool
keys=( D o c u m e )
run_xdotool
$sleep_big
clear_all

keys=( $cmd I g n o r e s space f i l e s space g i t i g n o r e space s t y l e )
run_xdotool
$sleep_big
clear_all

keys=( $cmd M a t c h e s space f i l e s space U n i x space s t y l e )
run_xdotool
$sleep_big
clear_all

keys=( $cmd asterisk period p n g )
run_xdotool
$sleep_big

keys=( BackSpace BackSpace BackSpace BackSpace BackSpace )
run_xdotool
keys=( t e s t asterisk period p y )
run_xdotool
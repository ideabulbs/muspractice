#!/bin/bash
#gst-launch-1.0 filesrc location=intro.mp4 ! decodebin2 name=dec ! queue ! ffmpegcolorspace ! autovideosink dec. ! queue ! audioconvert ! audioresample ! autoaudiosink
gst-launch-1.0 filesrc location=intro.mp4 ! decodebin name=dec ! queue ! autovideosink dec.  ! queue ! jackaudiosink

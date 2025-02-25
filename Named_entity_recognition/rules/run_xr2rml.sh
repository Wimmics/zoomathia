#!/bin/bash

# -- Example script to run xR2RML --

# Set the variables below first
XR2RML=tei

java -Xmx4g \
     -jar "morph-xr2rml-dist-1.3.1-jar-with-dependencies.jar" \
     --configDir $XR2RML \
     --configFile morph.properties

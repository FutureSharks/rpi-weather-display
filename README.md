# Raspberry Pi Weather Display

A small tool that gets weather forecasts from the internet and displays it on an e-ink display.

The e-ink display is a Waveshare 6inch HD model with a resolution of 1448*1072: https://www.waveshare.com/wiki/6inch_HD_e-Paper_HAT

Notable dependencies are:

1. The IT8951 driver to interface with the e-ink display: https://github.com/GregDMeyer/IT8951
2. A wrapper around the OpenWeatherMap web API: https://github.com/csparpa/pyowm

## Photos

Example display image:

<img src="https://raw.githubusercontent.com/FutureSharks/rpi-weather-display/master/img/display-example.png" width="800">

Photo of completed unit:

![complete](img/completed-1.jpg)

![complete](img/completed-2.jpg)

## Install

Install package requirements:

```console
apt update
apt install python3-pandas python3-pil python3-matplotlib
```

Then install this tool using pip:

```console
pip3 install https://github.com/FutureSharks/rpi-weather-display/archive/master.zip
```

And to optionally run it via cron:

```console
echo -e '#!/bin/sh\npgrep rpi-weather-display || rpi-weather-display --api-key <OMW API key>' > /etc/cron.hourly/rpi-weather-display
```

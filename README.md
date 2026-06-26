# Raspberry Pi Weather Display

A small tool that gets weather forecasts from the internet and displays it on an e-ink display.

The e-ink display is a Waveshare 6inch HD model with a resolution of 1448*1072: https://www.waveshare.com/wiki/6inch_HD_e-Paper_HAT

Notable dependencies are:

1. The IT8951 driver to interface with the e-ink display: [github.com/GregDMeyer/IT8951](https://github.com/GregDMeyer/IT8951)
2. A wrapper around the OpenWeatherMap web API: [github.com/csparpa/pyowm](https://github.com/csparpa/pyowm)
3. Weather icons: [github.com/erikflowers/weather-icons](https://github.com/erikflowers/weather-icons)

There is also a CAD model of an enclosure that can be 3D printed: [enclosure.stl](enclosure.stl)

Currently 2 weather providers are supported. They are both free but signup is required to get the necessary API key:

- [openweathermap.org/api](https://openweathermap.org/api)
- [tomorrow.io/weather-api](https://www.tomorrow.io/weather-api/)

## Photos

Example display image:

<img src="https://raw.githubusercontent.com/FutureSharks/rpi-weather-display/master/img/display-example.png" width="800">

Photo of completed unit:

![complete](img/completed-1.jpg)

![complete](img/completed-2.jpg)

![complete](img/completed-3.jpg)

## Install

Install package requirements using `apt` if running on a Raspberry Pi:

```console
apt update
apt install python3-pandas python3-pil python3-matplotlib python3-scipy python3-pip git pyenv
```

Since the `IT8951` module is old and not compatible with the latest versions of Pythong, we need to use pyenv to install Python 3.11:


```bash
export TMPDIR=/root/tmp
pyenv install 3.11
source .venv/bin/activate
pip3 install --break-system-packages https://github.com/FutureSharks/rpi-weather-display/archive/master.zip
```

 Then install this tool using pip:

```console
pip3 install --break-system-packages https://github.com/GregDMeyer/IT8951/archive/9f136139378f74e17d9972d7165dc6ae53a2568e.zip
pip3 install --break-system-packages https://github.com/FutureSharks/rpi-weather-display/archive/master.zip
```

And run it and it will update the e-ink display:

```console
rpi-weather-display --api-key <OMW API key>
```

And to optionally run it via cron:

```console
echo "/5 * * * * root pgrep rpi-weather-display > /dev/null || rpi-weather-display --api-key <API key> &" > /etc/cron.d/rpi-weather-display-start
```

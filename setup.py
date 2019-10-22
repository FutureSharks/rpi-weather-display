from setuptools import setup


setup(
    name="rpi-weather-display",
    version="1.0",
    url="https://github.com/FutureSharks/rpi-weather-display",
    license="GPL v3",
    description="A weather display using e-ink screen and a Raspberry Pi",
    long_description=open("README.md", encoding="utf-8").read(),
    packages=[
        "rpi_weather_display",
        "rpi_weather_display/plot",
        "rpi_weather_display/providers",
    ],
    entry_points={
        "console_scripts": ["rpi-weather-display=rpi_weather_display.cmd:main"],
    },
    install_requires=[
        "pyowm==3.1.1",
        "Pillow==7.2.0",
        "pandas==1.1.3",
        'IT8951 @ git+https://github.com/GregDMeyer/IT8951@a22e39299647a9e6d6299c64ff158cc6e2a96cd1#egg=IT8951'
    ],
)

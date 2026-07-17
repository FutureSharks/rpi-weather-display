# -*- coding: utf-8 -*-

_LAZY_IMAGE_ATTRS = {
    "create_hourly_image",
    "create_forecast_image",
    "create_error_image",
    "create_current_image",
    "create_daily_image",
}


def __getattr__(name):
    if name in _LAZY_IMAGE_ATTRS:
        from . import image

        return getattr(image, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

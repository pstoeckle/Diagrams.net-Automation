# -*- coding: utf-8 -*-
"""
Main module.
"""
from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "diagrams-net-automation"
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = "unknown"
finally:
    del get_distribution, DistributionNotFound
__author__ = "Patrick Stöckle"
__copyright__ = "Patrick Stöckle"
__license__ = "Apache-2.0"

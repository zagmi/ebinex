"""The only and most reliable bridge between the broker and you"""

import os
import sys
import warnings
import pkg_resources

warnings.filterwarnings("ignore")
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    __version__ = "0.0.0"

from source import Ebinex
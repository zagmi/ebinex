"""The only and most reliable bridge between the broker and you"""

import warnings
import pkg_resources

warnings.filterwarnings("ignore")

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    __version__ = "0.0.0"

from ebinexpy.source import Ebinex
__all__ = ["Ebinex", "__version__"]
"""PyLoader."""

from requests import get
from requests.exceptions import HTTPError as RequestHTTPError, ConnectionError as RequestConnectionError, MissingSchema, SSLError

from urllib.request import urlopen, urlretrieve
from urllib.error import HTTPError, URLError

from warnings import warn

from math import floor, log, pow

from time import perf_counter_ns

from typing import Union

from tempfile import gettempdir

from os import remove

from os.path import abspath

from uuid import uuid4


VERSION = 1.3

LOADING_GIF = abspath('pyloader\\media\\loading.gif')

def _percentage(current: int, maximal: int, _round: bool=False) -> int: return round((current / maximal) * 100) if _round else float(f'{((current / maximal) * 100):.1f}')

# https://stackoverflow.com/a/14822210/15277736 - Improved.
def _convsize(_bytes: int, chunk: int=1024) -> str: return '0b' if _bytes == 0 else '%s%s' % (round(_bytes / pow(chunk, int(floor(log(_bytes, chunk)))), 2), ('b', 'kb', 'mb', 'gb')[int(floor(log(_bytes, chunk)))])

class PyLoader:
    """PyLoader Class."""

    CHUNK = 1024

    temp_files: list[str] = []

    @staticmethod
    def download(url: str, out: str) -> bool:
        """Download file from URL."""
        try:
            urlretrieve(url, out)

            return True
        except HTTPError as httperror:
            warn(f'Failed to download from URL: "{url}".\nHTTPError: {httperror.status}.', stacklevel=2)

            return False

        except URLError as urlerror:
            if 'ssl' in str(urlerror.reason).lower():
                warn(f'Failed to download from URL: "{url}".\nFailed to verify SSL Certification (SSLCertVerificationError).', stacklevel=2)

            else:
                warn(f'Failed to download from URL: "{url}".\nURLError: {urlerror.reason}.', stacklevel=2)

            return False

        except ValueError:
            warn(f'Failed to download from URL: "{url}".\n ValueError: Unknown URL Type: "{url}".', stacklevel=2)

            return False

    @staticmethod
    def pdownload(url: str, out: str, round_progress: bool=False) -> dict:
        """Download file from URL with download information."""
        try:
            response = get(url, stream=True)

            total = int(urlopen(url).info()['Content-Length']) # || `response->headers.get:content-length, 0` ||
        except (HTTPError, RequestHTTPError) as httperror:
            warn(f'Failed to download from URL: "{url}" (pdownload).\nHTTPError: {httperror.status}. (Bad Request / Failed to get `Content-Length`).', stacklevel=2)

            yield False

            return

        except RequestConnectionError:
            warn(f'Failed to download from URL: "{url}" (pdownload).\nRequestConnectionError: No entities to download.', stacklevel=2)

            yield False

            return

        except MissingSchema:
            warn(f'Failed to download from URL: "{url}" (pdownload).\nMissingSchema: Wrong URL.', stacklevel=2)

            yield False

            return

        except SSLError:
            warn(f'Failed to download from URL: "{url}" (pdownload).\nFailed to verify SSL Certification.', stacklevel=2)

            yield False

            return

        current_progress = 0

        size = _convsize(total, PyLoader.CHUNK)

        with open(out, 'wb') as out_file:
            for data in response.iter_content(chunk_size=PyLoader.CHUNK):
                t_start = perf_counter_ns()

                size_written = out_file.write(data)

                current_progress += size_written

                yield {
                    'percentage': _percentage(current_progress, total, round_progress),
                    'current_progress': current_progress,
                    'size_written': size_written,
                    'size': size,
                    'totalbytes': total,
                    'chunk': PyLoader.CHUNK,
                    'time_wasted': f'{perf_counter_ns() - t_start}ns',
                    'success': True # XXX.
                }

    @staticmethod
    def webfile(url: str, _type: str) -> tuple[str, bool]:
        """Download web file buy URL and get path to downloaded web file."""
        path = f'{gettempdir()}\\{uuid4()}.{_type}'

        downloaded = PyLoader.download(url, path)

        PyLoader.temp_files.append(path)

        return (path, downloaded)

    @staticmethod
    def clear_temp_files() -> bool:
        """Clear temporary files created by `webfile`."""
        for temp_file in PyLoader.temp_files:
            try:
                remove(temp_file)

                PyLoader.temp_files.remove(temp_file)

                return True
            except:
                warn(f'Failed to remove temporary file: "{temp_file}".', stacklevel=2)

                return False

    @staticmethod
    def util_format(download_info: Union[bool, dict]) -> Union[bool, str]:
        """Utility for formating download information."""
        return download_info if isinstance(download_info, bool) else f'{download_info["percentage"]}/100% ({download_info["current_progress"]}/{download_info["totalbytes"]}b) [+{download_info["size_written"]} ({_convsize(download_info["size_written"])})] {_convsize(download_info["current_progress"], PyLoader.CHUNK)}/{download_info["size"]} C{download_info["chunk"]} {"S+" if download_info["success"] else "F-"} | {download_info["time_wasted"]}.'

    @staticmethod
    def update_chunk(new_chunk: int) -> None:
        """Update chunk."""
        PyLoader.CHUNK = new_chunk

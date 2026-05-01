from libprobe.probe import Probe
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = (
        ...,
    )

    probe = Probe("solarisilom", version, checks)

    probe.start()

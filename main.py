from libprobe.probe import Probe
from lib.check.solarisilom import CheckSolariosILOM
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = (
        CheckSolariosILOM,
    )

    probe = Probe("solarisilom", version, checks)

    probe.start()

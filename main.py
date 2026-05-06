from libprobe.probe import Probe
from lib.check.alarm import CheckAlarm
from lib.check.battery import CheckBattery
from lib.check.fan import CheckFan
from lib.check.power_supply import CheckPowerSupply
from lib.check.sensor import CheckSensor
from lib.check.solarisilom import CheckSolariosILOM
from lib.check.watchdog import CheckWatchdog
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = (
        CheckAlarm,
        CheckBattery,
        CheckFan,
        CheckPowerSupply,
        CheckSensor,
        CheckSolariosILOM,
        CheckWatchdog,
    )

    probe = Probe("solarisilom", version, checks)

    probe.start()

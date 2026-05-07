from asyncsnmplib.mib.mib_index import MIB_INDEX
from libprobe.asset import Asset
from libprobe.check import Check
from libprobe.exceptions import CheckException
from ..snmpclient import get_snmp_client
from ..snmpquery import snmpquery

QUERIES = (
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatMIBPhysicalObjects'], False),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatEquipmentEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatEquipmentHolderEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatCircuitPackEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatPhysicalEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatSensorEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatBinarySensorEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatNumericSensorEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatDiscreteSensorEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatDiscreteSensorStatesEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatFanEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatAlarmEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatWatchdogEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatPowerSupplyEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatBatteryEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatLogicalEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatUnitaryComputerSystemEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatInitialLoadInfoEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatLogEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatLogRecordEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatLogRecordAdditionalEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatLogRecordAlarmEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatLogRecordChangeEntry'], True),
)


class CheckSolariosILOM(Check):
    key = 'solarisilom'
    unchanged_eol = 14400

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        snmp = get_snmp_client(asset, local_config, config)
        state = await snmpquery(snmp, QUERIES)

        import pprint
        pprint.pprint(state)
        if not any(state.values()):
            raise CheckException('no data found')

        # we merge everything into single item
        # this is safe because we query only scalar objects
        item = {
            k: v
            for items in state.values()
            for item in items
            for k, v in item.items()
        }
        item['name'] = 'ilom'

        return {
            'ilom': [item]
        }

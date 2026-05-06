from asyncsnmplib.mib.mib_index import MIB_INDEX
from libprobe.asset import Asset
from libprobe.check import Check
from libprobe.exceptions import CheckException
from ..snmpclient import get_snmp_client
from ..snmpquery import snmpquery

QUERIES = (
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatMIBPhysicalObjects'], False),
    # (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatSensorEntry'], True),
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

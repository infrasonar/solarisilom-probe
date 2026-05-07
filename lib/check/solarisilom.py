from asyncsnmplib.mib.mib_index import MIB_INDEX
from libprobe.asset import Asset
from libprobe.check import Check
from libprobe.exceptions import CheckException
from ..snmpclient import get_snmp_client
from ..snmpquery import snmpquery

QUERIES = (
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatMIBPhysicalObjects'], False),
)


class CheckSolariosILOM(Check):
    key = 'solarisilom'
    unchanged_eol = 14400

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        snmp = get_snmp_client(asset, local_config, config)
        state = await snmpquery(snmp, QUERIES)

        if not state.get('sunPlatMIBPhysicalObjects'):
            raise CheckException('no data found')

        item = state['sunPlatMIBPhysicalObjects'][0]
        item['name'] = 'ilom'

        return {
            'ilom': [item]
        }

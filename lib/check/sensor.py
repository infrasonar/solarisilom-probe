import logging
from asyncsnmplib.mib.mib_index import MIB_INDEX
from libprobe.asset import Asset
from libprobe.check import Check
from ..snmpclient import get_snmp_client
from ..snmpquery import snmpquery

QUERIES = (
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatSensorEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatBinarySensorEntry'], True),
    (MIB_INDEX['SUN-PLATFORM-MIB']['sunPlatNumericSensorEntry'], True),
)

ENTPHYSICALDESCR_OID = MIB_INDEX['ENTITY-MIB']['entPhysicalDescr']
ENTITY_CACHE = {}


def on_sensor(item: dict):
    out = {
        'name': item['name'],
        'accuracy': item['sunPlatNumericSensorAccuracy'],
        'enabledThresholds':
            item['sunPlatNumericSensorEnabledThresholds'],
        'restoreDefaultThresholds':
            item['sunPlatNumericSensorRestoreDefaultThresholds'],
    }
    exp = item['sunPlatNumericSensorCurrent']
    for name, short in (
        ('sunPlatNumericSensorCurrent', 'value'),
        ('sunPlatNumericSensorNormalMin', 'normalMin'),
        ('sunPlatNumericSensorNormalMax', 'normalMax'),
        ('sunPlatNumericSensorLowerThresholdNonCritical',
         'lowerThresholdNonCritical'),
        ('sunPlatNumericSensorUpperThresholdNonCritical',
         'upperThresholdNonCritical'),
        ('sunPlatNumericSensorLowerThresholdCritical',
         'lowerThresholdCritical'),
        ('sunPlatNumericSensorUpperThresholdCritical',
         'upperThresholdCritical'),
        ('sunPlatNumericSensorLowerThresholdFatal',
         'lowerThresholdFatal'),
        ('sunPlatNumericSensorUpperThresholdFatal',
         'upperThresholdFatal'),
        ('sunPlatNumericSensorHysteresis', 'hysteresis'),
    ):
        out[short] = out[name] * 10 ** exp
    return out


class CheckSensor(Check):
    key = 'sensor'
    unchanged_eol = 14400

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        snmp = get_snmp_client(asset, local_config, config)

        if asset.id not in ENTITY_CACHE:
            varbinds = await snmp.walk(ENTPHYSICALDESCR_OID, False)
            ENTITY_CACHE[asset.id] = {
                # oid[-1] == entPhysicalIndex == item name
                str(oid[-1]): value
                for oid, value in varbinds
            }

        state = await snmpquery(snmp, QUERIES)

        # TODO also cache this?
        sensor_lk = {
            s['name']: {
                'class': s['sunPlatSensorClass'],
                'type': s['sunPlatSensorType'],
                'latency': s['sunPlatSensorLatency'],
                'entityDescr': ENTITY_CACHE[asset.id].get(s['name']),
            }
            for s in state['sunPlatSensorEntry']
        }

        sensor_bin = []
        for item in state['sunPlatBinarySensorEntry']:
            current = item['sunPlatBinarySensorCurrent']
            expected = item['sunPlatBinarySensorExpected']
            sensor_bin.append({
                'name': item['name'],
                'value': current != expected,
                **sensor_lk.get(item['name'], {}),
            })

        sensor_temperature = []
        sensor_amps = []
        sensor_volts = []
        sensor_watts = []
        sensor_rpm = []
        for item in state['sunPlatNumericSensorEntry']:
            s = sensor_lk.get(item['name'])
            if s:
                item.update(s)

            bu = item['sunPlatNumericSensorBaseUnits']
            match bu:
                case 'degC':
                    sensor_temperature.append(on_sensor(item))
                case 'amps':
                    sensor_amps.append(on_sensor(item))
                case 'volts':
                    sensor_volts.append(on_sensor(item))
                case 'watts':
                    sensor_watts.append(on_sensor(item))
                case 'rpm':
                    sensor_rpm.append(on_sensor(item))
                case _:
                    # TODO IncompleteResultException?
                    logging.warn(f'Unsupported sensor category: {bu}')

        return {
            'sensorBinary': sensor_bin,
            'sensorTemperature': sensor_temperature,
            'sensorAmps': sensor_amps,
            'sensorVolts': sensor_volts,
            'sensorWatts': sensor_watts,
            'sensorRPM': sensor_rpm,
        }

import logging
from asyncsnmplib.client import Snmp, SnmpV1, SnmpV3
from asyncsnmplib.v3.auth import AUTH_PROTO
from asyncsnmplib.v3.encr import PRIV_PROTO
from asyncsnmplib.v3.cache import SnmpV3Cache
from libprobe.asset import Asset
from libprobe.exceptions import CheckException
from . import DOCS_URL


class SnmpInvalidConfig(Exception):
    pass


V3_CACHE = {}


def get_snmp_client(
        asset: Asset,
        local_config: dict,
        config: dict) -> Snmp | SnmpV1 | SnmpV3:
    address = config.get('address')
    if not address:
        address = asset.name

    version = local_config.get('version', '2c')

    interval = config.get('_interval', 60)
    if interval <= 120:
        # for 2 minute or smaller intervals
        timeouts = (20, 10, 10)
    elif interval <= 240:
        # default for 3 and 4 minute intervals
        timeouts = (30, 20, 20)
    elif interval <= 540:
        # default for all between 5 and 10 minute intervals
        timeouts = (50, 50, 30, 30)
    else:
        # increased timeouts for 10 minute or larger intervals
        timeouts = (60, 60, 40, 40, 40)

    try:
        if version == '2c':
            community = local_config.get('community', 'public')
            if isinstance(community, dict):
                community = community.get('secret')
            if not isinstance(community, str):
                raise SnmpInvalidConfig('`community` must be a string.')
            cl = Snmp(
                host=address,
                community=community,
                timeouts=timeouts,
            )
        elif version == '3':
            username = local_config.get('username')
            if not isinstance(username, str):
                raise SnmpInvalidConfig('`username` must be a string.')
            auth = local_config.get('auth')
            if auth:
                auth_proto = AUTH_PROTO.get(auth.get('type'))
                auth_passwd = auth.get('password')
                if auth_proto is None:
                    raise SnmpInvalidConfig('`auth.type` invalid')
                elif not isinstance(auth_passwd, str):
                    raise SnmpInvalidConfig('`auth.password` must be string')
                auth = (auth_proto, auth_passwd)
            priv = auth and local_config.get('priv')
            if priv:
                priv_proto = PRIV_PROTO.get(priv.get('type'))
                priv_passwd = priv.get('password')
                if priv_proto is None:
                    raise SnmpInvalidConfig('`priv.type` invalid')
                elif not isinstance(priv_passwd, str):
                    raise SnmpInvalidConfig('`priv.password` must be string')
                priv = (priv_proto, priv_passwd)

            key = (asset.id, address, username, auth, priv)
            cache = V3_CACHE.get(key)
            if cache is None:
                V3_CACHE[key] = cache = SnmpV3Cache(username, auth, priv)

            cl = SnmpV3(
                host=address,
                username=username,
                auth=auth,
                priv=priv,
                cache=cache,
                timeouts=timeouts,
            )
        elif version == '1':
            community = local_config.get('community', 'public')
            if isinstance(community, dict):
                community = community.get('secret')
            if not isinstance(community, str):
                raise SnmpInvalidConfig('`community` must be a string.')
            cl = SnmpV1(
                host=address,
                community=community,
                timeouts=timeouts,
            )
        else:
            raise SnmpInvalidConfig(f'unsupported snmp version {version}')
    except SnmpInvalidConfig as e:
        msg = str(e) or type(e).__name__
        logging.error(f'Invalid config. Exception: {msg}')
        raise CheckException(
            'Invalid config. Please refer to the following documentation'
            f' for detailed instructions: <{DOCS_URL}>')

    return cl

import asyncio
import logging
from asyncsnmplib.client import Snmp, SnmpV1, SnmpV3
from asyncsnmplib.exceptions import (
    SnmpNoAuthParams, SnmpNoConnection, SnmpAuthV3Exception)
from asyncsnmplib.mib.utils import on_result, on_result_base
from libprobe.exceptions import CheckException
from typing import Any


async def _snmpquery(
    client: Snmp | SnmpV1 | SnmpV3,
    queries: tuple[tuple[tuple[int, ...], bool], ...],
    strip_metric_prefix: bool = False,
) -> dict[str, list[dict[str, Any]]]:
    '''Snmpwalk operation on the given oids

    Args:
        client:
            Snmp client
        queries:
            Tuple of Tuple with oid and is_table to query.
            Example: (((1.3.6.1.2.1.1), False),)
        strip_metric_prefix (bool, optional):
            Strip metric prefixes i.e. ipAddressOrigin -> Origin
            Defaults to False

    Returns:
        List of results grouped by name of the root oid
    '''
    _on_result = on_result if strip_metric_prefix else on_result_base

    try:
        await client.connect()
    except SnmpNoConnection:
        raise
    except SnmpNoAuthParams:
        logging.warning('unable to connect: failed to set auth params')
        raise
    else:
        results = {}
        for oid, is_table in queries:
            result = await client.walk(oid, is_table)
            try:
                name, result = _on_result(oid, result)
            except Exception as e:
                msg = str(e) or type(e).__name__
                raise CheckException(
                    f'Failed to parse result. Exception: {msg}')
            else:
                results[name] = result
        return results
    finally:
        # safe to close whatever the connection status is
        client.close()


async def snmpquery(
    client: Snmp | SnmpV1 | SnmpV3,
    queries: tuple[tuple[tuple[int, ...], bool], ...],
    strip_metric_prefix: bool = False,
) -> dict[str, list[dict[str, Any]]]:
    try:
        res = await _snmpquery(client, queries, strip_metric_prefix)
    except SnmpAuthV3Exception:
        await asyncio.sleep(1.0)
        # Retry...
        res = await _snmpquery(client, queries, strip_metric_prefix)

    return res

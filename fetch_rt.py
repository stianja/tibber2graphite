#!/usr/bin/env python3

import asyncio
import graphyte
from configparser import ConfigParser
from gql import Client, gql
from gql.transport.websockets import WebsocketsTransport
import os
from datetime import datetime


TIBBER_RT = "wss://websocket-api.tibber.com/v1-beta/gql/subscriptions"

# Load config
configfile = os.path.join(os.path.dirname(__file__) ,'etc', 'client.ini')
cp = ConfigParser()
cp.read(configfile)

TOKEN = cp.get('api', 'token')
HOME = cp.get('api', 'home')
USERAGENT = cp.get('api', 'useragent') 
GRAPHITEHOST = cp.get('graphite', 'host')
GRAPHITEPREFIX = cp.get('graphite', 'prefix')


def d2u(d):
    return int(datetime.fromisoformat(d).strftime('%s'))


def print_handle(data):
    prefix = "tibber.rt"
    d = data.get("liveMeasurement", {})
    ts = d2u(d['timestamp'])
    
    d['powerL1'] = 0
    d['powerL2'] = 0
    d['powerL3'] = 0


    if d['currentL1']:
        d['powerL1'] = d['currentL1'] * d['voltagePhase1']
        d['powerL2'] = d['currentL2'] * d['voltagePhase2']
        d['powerL3'] = d['currentL3'] * d['voltagePhase3']



 
    graphyte.init(GRAPHITEHOST)
    for addr in ['power', 'accumulatedConsumption', 'accumulatedCost', 'minPower', 'averagePower', 'maxPower', 'voltagePhase1', 'voltagePhase2', 'voltagePhase3', 'currentL1', 'currentL2', 'currentL3', 'powerL1', 'powerL2', 'powerL3']:
        if d[addr]:
            print('Sending %s %s %s' % (d['timestamp'], addr, d[addr]))
            graphyte.send('%s.%s' % (GRAPHITEPREFIX,addr), d[addr])


async def fetch_rt():
    transport = WebsocketsTransport(url=TIBBER_RT,
                                    init_payload={"token": TOKEN},
                                    headers={"User-Agent": USERAGENT},
                                    )

    async with Client(
        transport=transport,
        fetch_schema_from_transport=True,
    ) as session:

        query = """
        subscription{
        liveMeasurement(homeId:"%s"){
            timestamp
            power
            accumulatedConsumption
            accumulatedCost
            minPower
            averagePower
            maxPower
            voltagePhase1
            voltagePhase2
            voltagePhase3
            currentL1
            currentL2
            currentL3
            }
        }
        """ % HOME

        subscription = gql(query)
        async for result in session.subscribe(subscription):
            print_handle(result)

asyncio.run(fetch_rt())
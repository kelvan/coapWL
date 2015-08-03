import asyncio
import json

import aiocoap.resource as resource
import aiocoap
from pyWL.database import Station, Line
from pyWL.realtime import Departures
import json_serializer


class DepartureResource(resource.ObservableResource):
    def __init__(self):
        super().__init__()
        self.notify()

    def notify(self):
        self.updated_state()
        # Notify all observers every minute
        asyncio.get_event_loop().call_later(30, self.notify)

    @asyncio.coroutine
    def render_post(self, request):
        station_name = request.payload.decode('UTF-8')
        stations = Station.search_by_name(station_name)

        if len(station_name) < 4:
            payload = 'Search string to short'
            if len(station_name) == 0:
                payload = 'Missing search string'
            return aiocoap.Message(code=aiocoap.NOT_FOUND, payload=payload.encode('ascii'))

        if stations:
            payload = str([s['name'] for s in stations])
            for station in stations:
                if station['name'] == station_name:
                    stations = [station]

            if len(stations) == 1:
                station = stations[0]
                dep = Departures(station.get_stops())
                dep.refresh()
                payload = json.dumps(dep, ensure_ascii=False, default=json_serializer.default)
        else:
            return aiocoap.Message(code=aiocoap.NOT_FOUND, payload='Station not found'.encode('ascii'))

        return aiocoap.Message(code=aiocoap.CONTENT, payload=payload.encode('UTF-8'))


def main():
    root = resource.Site()
    # add .well-known/core
    wkc = resource.WKCResource(root.get_resources_as_linkheader)
    root.add_resource((".well-known", "core"), wkc)
    root.add_resource(("dep",), DepartureResource())

    asyncio.async(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()

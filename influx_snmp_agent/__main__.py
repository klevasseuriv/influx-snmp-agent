import time
import sys
from multiprocessing import Pool
from typing import Dict
import toml
from easysnmp import Session
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


def main():
    """Main loop"""

    config = toml.load(sys.argv[1])

    ifxclient = InfluxDBClient(
        url=config["influx"]["url"],
        token=config["influx"]["token"],
        org=config["influx"]["org"],
    )
    ifxwrite = ifxclient.write_api(write_options=SYNCHRONOUS)

    # I'm going to lose my mind
    for metric in config["metrics"]:
        metric["community"] = config["snmp"]["community"]

    while True:
        records = []
        with Pool(processes=4) as pool:
            records = pool.map(collect_proc, config["metrics"])
        if (len(records) < len(config["metrics"])) and (None not in records):
            print("Problem collecting some metrics")
            continue

        ifxwrite.write(bucket=config["influx"]["bucket"], record=records)
        time.sleep(int(config["snmp"]["rate"]))


def collect_proc(metric: Dict):
    """e"""
    session = Session(
        hostname=metric["host"],
        community=metric["community"],
        version=2,
    )

    oid_value = tryint(val=session.get(metric["oid"]).value)
    if oid_value is not None:
        return Point(metric["host_label"]).field(
            metric["metric_label"], float(oid_value)
        )
    return None


def tryint(val, default=None):
    try:
        return int(val)
    except ValueError:
        return default


if __name__ == "__main__":
    main()

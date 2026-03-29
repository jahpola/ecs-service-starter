import argparse
import sys

import boto3
from botocore.exceptions import ClientError
import logging

parser = argparse.ArgumentParser(prog="ecs-tasker", description="Starts/Stops ECS services")

parser.add_argument("--cluster", help="The name of the ECS cluster", required=True)
group1 = parser.add_mutually_exclusive_group(required=True)
group1.add_argument("--service", help="The name of the ECS service")
group1.add_argument("--all", help="Find all services", action="store_true")
group2 = parser.add_mutually_exclusive_group(required=True)
group2.add_argument("--stop", help="Stop the service", action="store_true")
group2.add_argument("--start", help="Start the service", action="store_true")
parser.add_argument(
    "--verbose",
    help="Enable verbose mode",
    action="store_const",
    dest="loglevel",
    default=logging.INFO,
    const=logging.DEBUG,
)


def stop_service(client, cluster, service):
    response = client.update_service(
        cluster=cluster,
        service=service,
        desiredCount=0,
    )
    logging.debug(response)


def start_service(client, cluster, service, desired_count=1):
    response = client.update_service(
        cluster=cluster,
        service=service,
        desiredCount=desired_count,
    )
    logging.debug(response)


def find_all_services(client, cluster):
    paginator = client.get_paginator("list_services")
    services = []
    for page in paginator.paginate(cluster=cluster):
        services.extend(page["serviceArns"])
    for service in services:
        logging.debug(service)
    return services


if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)

    client = boto3.client("ecs")
    cluster = args.cluster
    service = args.service
    stop = args.stop
    start = args.start

    try:
        if args.all:
            logging.info("Finding all services")
            services = find_all_services(client, cluster)
            logging.debug(services)
            for svc in services:
                if stop:
                    logging.info(f"Stopping service: {svc}")
                    stop_service(client, cluster, svc)
                elif start:
                    logging.info(f"Starting service: {svc}")
                    start_service(client, cluster, svc)
        elif start:
            logging.info(f"Starting service: {service}")
            start_service(client, cluster, service)
        else:
            logging.info(f"Stopping service: {service}")
            stop_service(client, cluster, service)
    except ClientError as e:
        logging.error(f"AWS error: {e.response['Error']['Message']}")
        sys.exit(1)

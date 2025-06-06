import argparse
import boto3
import logging

client = boto3.client("ecs", region_name="eu-north-1")

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


def stop_service(cluster, service):
    response = client.update_service(
        cluster=cluster,
        service=service,
        desiredCount=0,
    )
    logging.debug(response)


def start_service(cluster, service):
    response = client.update_service(
        cluster=cluster,
        service=service,
        desiredCount=1,
    )
    logging.debug(response)


def find_all_services(cluster):
    response = client.list_services(cluster=cluster, maxResults=100)
    services = response["serviceArns"]
    for service in services:
        logging.debug(service)
    return services


if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    logging.basicConfig(level=logging.DEBUG)

    cluster = args.cluster
    service = args.service
    stop = args.stop
    start = args.start

    if args.all:
        logging.info("Finding all services")
        services = find_all_services(cluster)
        logging.debug(services)
        for service in services:
            if stop:
                logging.info(f"Stopping service: {service}")
                stop_service(cluster, service)
            elif start:
                logging.info(f"Starting service: {service}")
                start_service(cluster, service)
    elif start:
        logging.info(f"Starting service: {service}")
        start_service(cluster, service)
    else:
        logging.info(f"Stopping service: {service}")
        stop_service(cluster, service)

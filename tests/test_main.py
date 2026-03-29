from unittest.mock import MagicMock

from main import find_all_services, start_service, stop_service


def test_stop_service_sets_desired_count_zero():
    client = MagicMock()
    stop_service(client, "my-cluster", "my-service")
    client.update_service.assert_called_once_with(cluster="my-cluster", service="my-service", desiredCount=0)


def test_start_service_default_desired_count():
    client = MagicMock()
    start_service(client, "my-cluster", "my-service")
    client.update_service.assert_called_once_with(cluster="my-cluster", service="my-service", desiredCount=1)


def test_start_service_custom_desired_count():
    client = MagicMock()
    start_service(client, "my-cluster", "my-service", desired_count=3)
    client.update_service.assert_called_once_with(cluster="my-cluster", service="my-service", desiredCount=3)


def test_find_all_services_single_page():
    client = MagicMock()
    paginator = MagicMock()
    client.get_paginator.return_value = paginator
    paginator.paginate.return_value = [{"serviceArns": ["arn:aws:ecs:eu-north-1:123:service/svc-1"]}]

    result = find_all_services(client, "my-cluster")

    client.get_paginator.assert_called_once_with("list_services")
    paginator.paginate.assert_called_once_with(cluster="my-cluster")
    assert result == ["arn:aws:ecs:eu-north-1:123:service/svc-1"]


def test_find_all_services_multiple_pages():
    client = MagicMock()
    paginator = MagicMock()
    client.get_paginator.return_value = paginator
    paginator.paginate.return_value = [
        {"serviceArns": ["arn:aws:ecs:eu-north-1:123:service/svc-1"]},
        {"serviceArns": ["arn:aws:ecs:eu-north-1:123:service/svc-2", "arn:aws:ecs:eu-north-1:123:service/svc-3"]},
    ]

    result = find_all_services(client, "my-cluster")

    assert result == [
        "arn:aws:ecs:eu-north-1:123:service/svc-1",
        "arn:aws:ecs:eu-north-1:123:service/svc-2",
        "arn:aws:ecs:eu-north-1:123:service/svc-3",
    ]


def test_find_all_services_empty():
    client = MagicMock()
    paginator = MagicMock()
    client.get_paginator.return_value = paginator
    paginator.paginate.return_value = [{"serviceArns": []}]

    result = find_all_services(client, "my-cluster")

    assert result == []

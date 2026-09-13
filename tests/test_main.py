"""Unit tests for ECS service management functions."""

import logging
import runpy
import sys

import pytest
from botocore.exceptions import ClientError

from main import find_all_services, start_service, stop_service


class TestStopService:
    """Tests for stop_service function."""

    def test_sets_desired_count_to_zero(self, ecs_client):
        """Verify that stop_service sets desiredCount to 0."""
        stop_service(ecs_client, "my-cluster", "my-service")
        ecs_client.update_service.assert_called_once_with(cluster="my-cluster", service="my-service", desiredCount=0)


class TestStartService:
    """Tests for start_service function."""

    @pytest.mark.parametrize("desired_count,expected", [(None, 1), (3, 3), (5, 5)])
    def test_sets_desired_count(self, ecs_client, desired_count, expected):
        """Verify that start_service sets desiredCount correctly."""
        if desired_count is None:
            start_service(ecs_client, "my-cluster", "my-service")
        else:
            start_service(ecs_client, "my-cluster", "my-service", desired_count=desired_count)

        ecs_client.update_service.assert_called_once_with(
            cluster="my-cluster", service="my-service", desiredCount=expected
        )


class TestFindAllServices:
    """Tests for find_all_services function."""

    def test_single_page_result(self, ecs_client_with_paginator):
        """Verify that single page results are correctly retrieved."""
        ecs_client = ecs_client_with_paginator
        paginator = ecs_client.get_paginator.return_value
        paginator.paginate.return_value = [{"serviceArns": ["arn:aws:ecs:eu-north-1:123:service/svc-1"]}]

        result = find_all_services(ecs_client, "my-cluster")

        ecs_client.get_paginator.assert_called_once_with("list_services")
        paginator.paginate.assert_called_once_with(cluster="my-cluster")
        assert result == ["arn:aws:ecs:eu-north-1:123:service/svc-1"]

    def test_multiple_pages_result(self, ecs_client_with_paginator):
        """Verify that multiple pages are correctly aggregated."""
        ecs_client = ecs_client_with_paginator
        paginator = ecs_client.get_paginator.return_value
        paginator.paginate.return_value = [
            {"serviceArns": ["arn:aws:ecs:eu-north-1:123:service/svc-1"]},
            {"serviceArns": ["arn:aws:ecs:eu-north-1:123:service/svc-2", "arn:aws:ecs:eu-north-1:123:service/svc-3"]},
        ]

        result = find_all_services(ecs_client, "my-cluster")

        assert result == [
            "arn:aws:ecs:eu-north-1:123:service/svc-1",
            "arn:aws:ecs:eu-north-1:123:service/svc-2",
            "arn:aws:ecs:eu-north-1:123:service/svc-3",
        ]

    def test_empty_result(self, ecs_client_with_paginator):
        """Verify that empty service list is handled correctly."""
        ecs_client = ecs_client_with_paginator
        paginator = ecs_client.get_paginator.return_value
        paginator.paginate.return_value = [{"serviceArns": []}]

        result = find_all_services(ecs_client, "my-cluster")

        assert result == []


class TestCli:
    """Tests for CLI execution."""

    def test_client_error_logs_and_exits(self, monkeypatch, caplog):
        """Verify CLI logs ECS client errors and exits with a non-zero status."""

        def raise_client_error(*args, **kwargs):
            raise ClientError(
                {"Error": {"Code": "AccessDeniedException", "Message": "Access denied"}},
                "UpdateService",
            )

        monkeypatch.setattr("boto3.client", raise_client_error)
        monkeypatch.setattr(
            sys,
            "argv",
            ["main.py", "--cluster", "my-cluster", "--service", "my-service", "--start"],
        )

        with caplog.at_level(logging.ERROR), pytest.raises(SystemExit) as exc_info:
            runpy.run_module("main", run_name="__main__")

        assert exc_info.value.code == 1
        assert "AWS error: Access denied" in caplog.text

"""Shared test fixtures and configuration."""
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def ecs_client():
    """Provide a mock ECS client for testing."""
    return MagicMock()


@pytest.fixture
def mock_paginator():
    """Provide a mock paginator for list_services."""
    paginator = MagicMock()
    return paginator


@pytest.fixture
def ecs_client_with_paginator(ecs_client, mock_paginator):
    """Provide an ECS client with a configured paginator."""
    ecs_client.get_paginator.return_value = mock_paginator
    return ecs_client

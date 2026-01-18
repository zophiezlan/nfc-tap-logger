"""
Service Configuration Integration

This module integrates the service configuration system with the existing codebase,
providing backward compatibility while enabling full configurability for different
festival drug checking services.

It provides helper functions that abstract away hardcoded stage names and allow
the system to work with custom workflows defined in service_config.yaml.
"""

import sys
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

# Add parent directory to path to import service_config_loader
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from service_config_loader import get_service_config, ServiceConfig
    SERVICE_CONFIG_AVAILABLE = True
except ImportError:
    logger.warning("service_config_loader not available, using defaults")
    SERVICE_CONFIG_AVAILABLE = False


class ServiceIntegration:
    """
    Integration layer between service configuration and existing codebase.

    This class provides methods to access service-specific configuration
    while maintaining backward compatibility with hardcoded values.
    """

    def __init__(self):
        """Initialize service integration"""
        self._config: Optional[ServiceConfig] = None
        self._load_config()

    def _load_config(self):
        """Load service configuration"""
        if SERVICE_CONFIG_AVAILABLE:
            try:
                self._config = get_service_config()
                logger.info(f"Service configuration loaded: {self._config.service_name}")
            except Exception as e:
                logger.error(f"Failed to load service config: {e}")
                self._config = None
        else:
            self._config = None

    # -------------------------------------------------------------------------
    # Stage Management
    # -------------------------------------------------------------------------

    def get_first_stage(self) -> str:
        """
        Get the ID of the first stage in the workflow.
        This is typically the queue join stage.

        Returns:
            Stage ID (default: "QUEUE_JOIN")
        """
        if self._config and self._config.workflow_stages:
            return self._config.workflow_stages[0].id
        return "QUEUE_JOIN"

    def get_last_stage(self) -> str:
        """
        Get the ID of the last stage in the workflow.
        This is typically the exit stage.

        Returns:
            Stage ID (default: "EXIT")
        """
        if self._config and self._config.workflow_stages:
            return self._config.workflow_stages[-1].id
        return "EXIT"

    def get_service_start_stage(self) -> Optional[str]:
        """
        Get the ID of the service start stage, if it exists.

        Returns:
            Stage ID if found, None otherwise (default: "SERVICE_START" if in config)
        """
        if self._config:
            for stage in self._config.workflow_stages:
                if stage.id == "SERVICE_START":
                    return stage.id
            # If there's a middle stage, return it
            if len(self._config.workflow_stages) > 2:
                return self._config.workflow_stages[1].id
        return "SERVICE_START"  # Default for backward compatibility

    def get_all_stage_ids(self) -> List[str]:
        """
        Get all stage IDs in workflow order.

        Returns:
            List of stage IDs
        """
        if self._config:
            return self._config.get_all_stage_ids()
        return ["QUEUE_JOIN", "SERVICE_START", "EXIT"]

    def get_stage_label(self, stage_id: str) -> str:
        """
        Get human-readable label for a stage.

        Args:
            stage_id: Stage identifier

        Returns:
            Display label for the stage
        """
        if self._config:
            return self._config.get_stage_label(stage_id)

        # Default labels
        labels = {
            "QUEUE_JOIN": "In Queue",
            "SERVICE_START": "Being Served",
            "EXIT": "Completed",
        }
        return labels.get(stage_id, stage_id)

    def get_stage_labels_map(self) -> Dict[str, str]:
        """
        Get a mapping of stage IDs to display labels.

        Returns:
            Dictionary of {stage_id: label}
        """
        if self._config:
            return {
                stage.id: stage.label
                for stage in self._config.workflow_stages
            }

        return {
            "QUEUE_JOIN": "In Queue",
            "SERVICE_START": "Being Served",
            "EXIT": "Completed",
        }

    def has_service_start_stage(self) -> bool:
        """
        Check if the workflow includes a service start stage.

        Returns:
            True if SERVICE_START or equivalent exists
        """
        if self._config:
            # Check if there are more than 2 stages (more than just join and exit)
            return len(self._config.workflow_stages) > 2
        return True  # Default assumes SERVICE_START exists

    # -------------------------------------------------------------------------
    # Capacity & Throughput
    # -------------------------------------------------------------------------

    def get_people_per_hour(self) -> int:
        """Get configured service capacity (people per hour)"""
        if self._config:
            return self._config.people_per_hour
        return 12  # Default

    def get_avg_service_minutes(self) -> int:
        """Get average service time in minutes"""
        if self._config:
            return self._config.avg_service_minutes
        return 5  # Default

    def get_default_wait_estimate(self) -> int:
        """Get default wait time estimate in minutes"""
        if self._config:
            return self._config.default_wait_estimate
        return 20  # Default

    def get_queue_multiplier(self) -> int:
        """Get queue position multiplier for wait estimation"""
        if self._config:
            return self._config.queue_multiplier
        return 2  # Default

    # -------------------------------------------------------------------------
    # Alert Thresholds
    # -------------------------------------------------------------------------

    def get_queue_warning_threshold(self) -> int:
        """Get queue length warning threshold"""
        if self._config:
            return self._config.queue_warning_threshold
        return 10

    def get_queue_critical_threshold(self) -> int:
        """Get queue length critical threshold"""
        if self._config:
            return self._config.queue_critical_threshold
        return 20

    def get_wait_warning_minutes(self) -> int:
        """Get wait time warning threshold (minutes)"""
        if self._config:
            return self._config.wait_warning_minutes
        return 45

    def get_wait_critical_minutes(self) -> int:
        """Get wait time critical threshold (minutes)"""
        if self._config:
            return self._config.wait_critical_minutes
        return 90

    def get_service_inactivity_warning_minutes(self) -> int:
        """Get service inactivity warning threshold (minutes)"""
        if self._config:
            return self._config.service_inactivity_warning_minutes
        return 5

    def get_service_inactivity_critical_minutes(self) -> int:
        """Get service inactivity critical threshold (minutes)"""
        if self._config:
            return self._config.service_inactivity_critical_minutes
        return 10

    def get_stuck_cards_threshold_hours(self) -> int:
        """Get stuck cards threshold (hours)"""
        if self._config:
            return self._config.stuck_cards_threshold_hours
        return 2

    def get_service_variance_multiplier(self) -> int:
        """Get service time variance multiplier"""
        if self._config:
            return self._config.service_variance_multiplier
        return 3

    def get_capacity_critical_percent(self) -> int:
        """Get capacity utilization critical threshold (%)"""
        if self._config:
            return self._config.capacity_critical_percent
        return 90

    def get_temperature_critical_celsius(self) -> int:
        """Get temperature critical threshold (°C)"""
        if self._config:
            return self._config.temperature_critical_celsius
        return 80

    def get_disk_warning_percent(self) -> int:
        """Get disk usage warning threshold (%)"""
        if self._config:
            return self._config.disk_warning_percent
        return 80

    def get_disk_critical_percent(self) -> int:
        """Get disk usage critical threshold (%)"""
        if self._config:
            return self._config.disk_critical_percent
        return 90

    # -------------------------------------------------------------------------
    # UI Labels & Messages
    # -------------------------------------------------------------------------

    def get_service_name(self) -> str:
        """Get service name for display"""
        if self._config:
            return self._config.service_name
        return "Drug Checking Service"

    def get_ui_label(self, key: str, default: str = None) -> str:
        """
        Get a UI label by key.

        Args:
            key: Label key (e.g., 'queue_count', 'wait_time')
            default: Default value if not found

        Returns:
            Label text
        """
        if self._config:
            return self._config.get_ui_label(key, default)

        # Default labels
        defaults = {
            'queue_count': 'people in queue',
            'wait_time': 'estimated wait',
            'served_today': 'served today',
            'avg_service_time': 'avg service time',
            'service_status': 'service status',
            'status_active': 'ACTIVE',
            'status_idle': 'IDLE',
            'status_stopped': 'STOPPED',
        }
        return defaults.get(key, default or key)

    def get_alert_message(self, key: str, **kwargs) -> str:
        """
        Get a formatted alert message.

        Args:
            key: Message key
            **kwargs: Formatting parameters

        Returns:
            Formatted message text
        """
        if self._config:
            return self._config.get_alert_message(key, **kwargs)

        # Default messages
        defaults = {
            'queue_warning': 'Queue is getting long ({count} people)',
            'queue_critical': 'Queue is very long ({count} people) - consider adding staff',
            'wait_warning': 'Estimated wait time is high ({minutes} min)',
            'wait_critical': 'Estimated wait time is very high ({minutes} min)',
            'inactivity_warning': 'No service activity for {minutes} minutes',
            'inactivity_critical': 'Service appears stopped - no activity for {minutes} minutes',
        }
        template = defaults.get(key, "")
        try:
            return template.format(**kwargs)
        except KeyError:
            return template

    # -------------------------------------------------------------------------
    # Display Settings
    # -------------------------------------------------------------------------

    def get_public_refresh_interval(self) -> int:
        """Get public display refresh interval (seconds)"""
        if self._config:
            return self._config.public_refresh_interval
        return 5

    def show_queue_positions(self) -> bool:
        """Should queue positions be shown on public display?"""
        if self._config:
            return self._config.show_queue_positions
        return True

    def show_wait_estimates(self) -> bool:
        """Should wait estimates be shown on public display?"""
        if self._config:
            return self._config.show_wait_estimates
        return True

    def show_served_count(self) -> bool:
        """Should served count be shown on public display?"""
        if self._config:
            return self._config.show_served_count
        return True

    def show_avg_time(self) -> bool:
        """Should average service time be shown on public display?"""
        if self._config:
            return self._config.show_avg_time
        return True

    def get_max_recent_events(self) -> int:
        """Get max number of recent events to show"""
        if self._config:
            return self._config.max_recent_events
        return 15

    def get_max_recent_completions(self) -> int:
        """Get max number of recent completions to show"""
        if self._config:
            return self._config.max_recent_completions
        return 10

    def get_analytics_history_hours(self) -> int:
        """Get analytics history window (hours)"""
        if self._config:
            return self._config.analytics_history_hours
        return 12

    def get_wait_time_sample_size(self) -> int:
        """Get sample size for wait time calculations"""
        if self._config:
            return self._config.wait_time_sample_size
        return 20

    def get_shift_summary_hours(self) -> int:
        """Get shift summary window (hours)"""
        if self._config:
            return self._config.shift_summary_hours
        return 4

    # -------------------------------------------------------------------------
    # Raw Configuration Access
    # -------------------------------------------------------------------------

    def get_raw_config(self, path: str, default: Any = None) -> Any:
        """
        Get a value from raw configuration using dot notation.

        Args:
            path: Dot-separated path (e.g., 'integrations.webhooks.enabled')
            default: Default value if not found

        Returns:
            Configuration value or default
        """
        if self._config:
            return self._config.get_raw(path, default)
        return default

    def has_config(self) -> bool:
        """Check if service configuration is loaded"""
        return self._config is not None


# Global service integration instance
_service_integration: Optional[ServiceIntegration] = None


def get_service_integration() -> ServiceIntegration:
    """
    Get the global service integration instance (singleton).

    Returns:
        ServiceIntegration instance
    """
    global _service_integration

    if _service_integration is None:
        _service_integration = ServiceIntegration()

    return _service_integration


# Convenience functions for common operations
def get_first_stage() -> str:
    """Get the first stage ID (typically QUEUE_JOIN)"""
    return get_service_integration().get_first_stage()


def get_last_stage() -> str:
    """Get the last stage ID (typically EXIT)"""
    return get_service_integration().get_last_stage()


def get_service_start_stage() -> Optional[str]:
    """Get the service start stage ID (if it exists)"""
    return get_service_integration().get_service_start_stage()


def get_stage_label(stage_id: str) -> str:
    """Get the display label for a stage"""
    return get_service_integration().get_stage_label(stage_id)


def get_ui_label(key: str, default: str = None) -> str:
    """Get a UI label by key"""
    return get_service_integration().get_ui_label(key, default)


if __name__ == "__main__":
    # Test the service integration
    logging.basicConfig(level=logging.INFO)

    integration = get_service_integration()

    print(f"\nService: {integration.get_service_name()}")
    print(f"\nWorkflow Stages:")
    print(f"  First: {integration.get_first_stage()} ({integration.get_stage_label(integration.get_first_stage())})")
    if integration.has_service_start_stage():
        svc_stage = integration.get_service_start_stage()
        print(f"  Service: {svc_stage} ({integration.get_stage_label(svc_stage)})")
    print(f"  Last: {integration.get_last_stage()} ({integration.get_stage_label(integration.get_last_stage())})")

    print(f"\nCapacity:")
    print(f"  {integration.get_people_per_hour()} people/hour")
    print(f"  {integration.get_avg_service_minutes()} min average")

    print(f"\nAlert Thresholds:")
    print(f"  Queue: {integration.get_queue_warning_threshold()} warn, {integration.get_queue_critical_threshold()} critical")
    print(f"  Wait: {integration.get_wait_warning_minutes()} warn, {integration.get_wait_critical_minutes()} critical min")

    print(f"\nUI Labels:")
    print(f"  Queue: {integration.get_ui_label('queue_count')}")
    print(f"  Wait: {integration.get_ui_label('wait_time')}")
    print(f"  Served: {integration.get_ui_label('served_today')}")

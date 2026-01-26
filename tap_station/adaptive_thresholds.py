"""
Adaptive Thresholds System

This module provides context-aware, dynamic thresholds that adapt based on:
- Time of day (peak vs off-peak hours)
- Day of week patterns
- Historical performance
- Current conditions
- Staff capacity

Key Features:
- Time-based threshold adjustments
- Learning from historical patterns
- Manual override support
- Threshold explanation system
- Service design focus on appropriate alerting

Service Design Principles:
- Alert fatigue reduction through smart thresholds
- Context-appropriate expectations
- Data-driven threshold optimization
"""

import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from .datetime_utils import utc_now

logger = logging.getLogger(__name__)


class ThresholdType(Enum):
    """Types of thresholds"""

    QUEUE_WARNING = "queue_warning"
    QUEUE_CRITICAL = "queue_critical"
    WAIT_WARNING = "wait_warning"
    WAIT_CRITICAL = "wait_critical"
    THROUGHPUT_WARNING = "throughput_warning"
    THROUGHPUT_CRITICAL = "throughput_critical"
    INACTIVITY_WARNING = "inactivity_warning"
    INACTIVITY_CRITICAL = "inactivity_critical"
    SERVICE_TIME_WARNING = "service_time_warning"
    SERVICE_TIME_CRITICAL = "service_time_critical"


class AdjustmentReason(Enum):
    """Reasons for threshold adjustments"""

    PEAK_HOURS = "peak_hours"
    OFF_PEAK = "off_peak"
    HIGH_DEMAND = "high_demand"
    LOW_DEMAND = "low_demand"
    STAFFING_LEVEL = "staffing_level"
    HISTORICAL_PATTERN = "historical_pattern"
    MANUAL_OVERRIDE = "manual_override"
    SYSTEM_DEFAULT = "system_default"


@dataclass
class TimeWindow:
    """Represents a time window for threshold adjustments"""

    start: time
    end: time
    days: List[int] = field(
        default_factory=lambda: list(range(7))
    )  # 0=Monday, 6=Sunday
    label: str = ""

    def contains(self, dt: datetime) -> bool:
        """Check if datetime falls within this window"""
        if dt.weekday() not in self.days:
            return False

        current_time = dt.time()

        # Handle windows that cross midnight
        if self.start <= self.end:
            return self.start <= current_time <= self.end
        else:
            return current_time >= self.start or current_time <= self.end

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "days": self.days,
            "label": self.label,
        }


@dataclass
class ThresholdAdjustment:
    """An adjustment to a threshold"""

    threshold_type: ThresholdType
    base_value: float
    adjusted_value: float
    multiplier: float
    reason: AdjustmentReason
    explanation: str
    active_until: Optional[datetime] = None
    priority: int = 0  # Higher = takes precedence

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "threshold_type": self.threshold_type.value,
            "base_value": self.base_value,
            "adjusted_value": self.adjusted_value,
            "multiplier": self.multiplier,
            "reason": self.reason.value,
            "explanation": self.explanation,
            "active_until": (
                self.active_until.isoformat() if self.active_until else None
            ),
            "priority": self.priority,
        }


@dataclass
class ThresholdRule:
    """A rule for adjusting thresholds"""

    id: str
    name: str
    description: str
    threshold_types: List[ThresholdType]
    multiplier: float
    condition: Callable[[datetime, Dict[str, Any]], bool]
    reason: AdjustmentReason
    priority: int = 0
    enabled: bool = True
    time_windows: List[TimeWindow] = field(default_factory=list)

    def evaluate(self, dt: datetime, context: Dict[str, Any]) -> bool:
        """Evaluate if this rule applies"""
        if not self.enabled:
            return False

        # Check time windows if defined
        if self.time_windows:
            if not any(w.contains(dt) for w in self.time_windows):
                return False

        # Check custom condition
        return self.condition(dt, context)


@dataclass
class ThresholdConfig:
    """Configuration for a threshold"""

    threshold_type: ThresholdType
    base_value: float
    min_value: float
    max_value: float
    unit: str
    description: str


class AdaptiveThresholdManager:
    """
    Manages context-aware, adaptive thresholds.

    This manager adjusts thresholds based on various factors while
    ensuring alerts remain meaningful and actionable.
    """

    # Default base thresholds
    DEFAULT_THRESHOLDS = {
        ThresholdType.QUEUE_WARNING: ThresholdConfig(
            ThresholdType.QUEUE_WARNING,
            10,
            5,
            30,
            "people",
            "Queue length warning threshold",
        ),
        ThresholdType.QUEUE_CRITICAL: ThresholdConfig(
            ThresholdType.QUEUE_CRITICAL,
            20,
            10,
            50,
            "people",
            "Queue length critical threshold",
        ),
        ThresholdType.WAIT_WARNING: ThresholdConfig(
            ThresholdType.WAIT_WARNING,
            30,
            15,
            90,
            "minutes",
            "Wait time warning threshold",
        ),
        ThresholdType.WAIT_CRITICAL: ThresholdConfig(
            ThresholdType.WAIT_CRITICAL,
            60,
            30,
            120,
            "minutes",
            "Wait time critical threshold",
        ),
        ThresholdType.THROUGHPUT_WARNING: ThresholdConfig(
            ThresholdType.THROUGHPUT_WARNING,
            6,
            3,
            20,
            "per_hour",
            "Minimum throughput warning threshold",
        ),
        ThresholdType.THROUGHPUT_CRITICAL: ThresholdConfig(
            ThresholdType.THROUGHPUT_CRITICAL,
            3,
            1,
            10,
            "per_hour",
            "Minimum throughput critical threshold",
        ),
        ThresholdType.INACTIVITY_WARNING: ThresholdConfig(
            ThresholdType.INACTIVITY_WARNING,
            10,
            5,
            30,
            "minutes",
            "Service inactivity warning threshold",
        ),
        ThresholdType.INACTIVITY_CRITICAL: ThresholdConfig(
            ThresholdType.INACTIVITY_CRITICAL,
            20,
            10,
            60,
            "minutes",
            "Service inactivity critical threshold",
        ),
        ThresholdType.SERVICE_TIME_WARNING: ThresholdConfig(
            ThresholdType.SERVICE_TIME_WARNING,
            15,
            5,
            45,
            "minutes",
            "Individual service time warning threshold",
        ),
        ThresholdType.SERVICE_TIME_CRITICAL: ThresholdConfig(
            ThresholdType.SERVICE_TIME_CRITICAL,
            30,
            15,
            90,
            "minutes",
            "Individual service time critical threshold",
        ),
    }

    def __init__(
        self,
        conn: Optional[sqlite3.Connection] = None,
        base_thresholds: Optional[Dict[ThresholdType, float]] = None,
    ):
        """
        Initialize the adaptive threshold manager.

        Args:
            conn: Database connection for historical analysis
            base_thresholds: Custom base threshold values
        """
        self._conn = conn
        self._configs = self.DEFAULT_THRESHOLDS.copy()
        self._rules: List[ThresholdRule] = []
        self._manual_overrides: Dict[ThresholdType, ThresholdAdjustment] = {}
        self._current_adjustments: Dict[ThresholdType, ThresholdAdjustment] = (
            {}
        )

        # Apply custom base thresholds
        if base_thresholds:
            for t_type, value in base_thresholds.items():
                if t_type in self._configs:
                    self._configs[t_type].base_value = value

        # Load default rules
        self._load_default_rules()

    def _load_default_rules(self) -> None:
        """Load the default threshold adjustment rules"""
        # Peak hours rule - more lenient thresholds
        self._rules.append(
            ThresholdRule(
                id="peak_hours",
                name="Peak Hours Adjustment",
                description="Increase thresholds during peak demand hours",
                threshold_types=[
                    ThresholdType.QUEUE_WARNING,
                    ThresholdType.QUEUE_CRITICAL,
                    ThresholdType.WAIT_WARNING,
                    ThresholdType.WAIT_CRITICAL,
                ],
                multiplier=1.3,
                condition=lambda dt, ctx: True,  # Time window handles the condition
                reason=AdjustmentReason.PEAK_HOURS,
                priority=10,
                time_windows=[
                    TimeWindow(
                        time(20, 0), time(23, 59), label="Evening peak"
                    ),
                    TimeWindow(
                        time(14, 0), time(18, 0), label="Afternoon peak"
                    ),
                ],
            )
        )

        # Off-peak rule - stricter thresholds
        self._rules.append(
            ThresholdRule(
                id="off_peak",
                name="Off-Peak Adjustment",
                description="Decrease thresholds during quiet periods",
                threshold_types=[
                    ThresholdType.QUEUE_WARNING,
                    ThresholdType.QUEUE_CRITICAL,
                    ThresholdType.INACTIVITY_WARNING,
                    ThresholdType.INACTIVITY_CRITICAL,
                ],
                multiplier=0.8,
                condition=lambda dt, ctx: True,
                reason=AdjustmentReason.OFF_PEAK,
                priority=10,
                time_windows=[
                    TimeWindow(
                        time(10, 0), time(13, 0), label="Morning quiet"
                    ),
                ],
            )
        )

        # High demand context rule
        self._rules.append(
            ThresholdRule(
                id="high_demand",
                name="High Demand Adjustment",
                description="Adjust thresholds when demand exceeds normal levels",
                threshold_types=[
                    ThresholdType.QUEUE_WARNING,
                    ThresholdType.QUEUE_CRITICAL,
                    ThresholdType.WAIT_WARNING,
                    ThresholdType.WAIT_CRITICAL,
                ],
                multiplier=1.25,
                condition=lambda dt, ctx: ctx.get("demand_level", "normal")
                == "high",
                reason=AdjustmentReason.HIGH_DEMAND,
                priority=20,
            )
        )

        # Low staffing rule
        self._rules.append(
            ThresholdRule(
                id="low_staffing",
                name="Low Staffing Adjustment",
                description="Adjust thresholds when fewer staff are available",
                threshold_types=[
                    ThresholdType.THROUGHPUT_WARNING,
                    ThresholdType.THROUGHPUT_CRITICAL,
                ],
                multiplier=0.7,
                condition=lambda dt, ctx: ctx.get("staff_count", 2) < 2,
                reason=AdjustmentReason.STAFFING_LEVEL,
                priority=25,
            )
        )

    def configure_base_threshold(
        self, threshold_type: ThresholdType, value: float
    ) -> None:
        """Configure a base threshold value"""
        if threshold_type in self._configs:
            config = self._configs[threshold_type]
            # Clamp to valid range
            value = max(config.min_value, min(config.max_value, value))
            config.base_value = value
            logger.info(
                f"Base threshold {threshold_type.value} set to {value}"
            )

    def add_rule(self, rule: ThresholdRule) -> None:
        """Add a custom threshold adjustment rule"""
        self._rules.append(rule)
        self._rules.sort(key=lambda r: -r.priority)
        logger.info(f"Added threshold rule: {rule.id}")

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a threshold rule by ID"""
        original_count = len(self._rules)
        self._rules = [r for r in self._rules if r.id != rule_id]
        removed = len(self._rules) < original_count
        if removed:
            logger.info(f"Removed threshold rule: {rule_id}")
        return removed

    def set_manual_override(
        self,
        threshold_type: ThresholdType,
        value: float,
        duration_minutes: Optional[int] = None,
        reason: str = "",
    ) -> ThresholdAdjustment:
        """
        Set a manual override for a threshold.

        Args:
            threshold_type: Threshold to override
            value: New threshold value
            duration_minutes: How long the override lasts (None = permanent)
            reason: Explanation for the override

        Returns:
            The created adjustment
        """
        config = self._configs.get(threshold_type)
        if not config:
            raise ValueError(f"Unknown threshold type: {threshold_type}")

        active_until = None
        if duration_minutes:
            active_until = utc_now() + timedelta(minutes=duration_minutes)

        adjustment = ThresholdAdjustment(
            threshold_type=threshold_type,
            base_value=config.base_value,
            adjusted_value=value,
            multiplier=(
                value / config.base_value if config.base_value > 0 else 1
            ),
            reason=AdjustmentReason.MANUAL_OVERRIDE,
            explanation=reason or f"Manual override to {value} {config.unit}",
            active_until=active_until,
            priority=100,  # Highest priority
        )

        self._manual_overrides[threshold_type] = adjustment
        logger.info(f"Manual override set: {threshold_type.value} = {value}")
        return adjustment

    def clear_manual_override(self, threshold_type: ThresholdType) -> bool:
        """Clear a manual override"""
        if threshold_type in self._manual_overrides:
            del self._manual_overrides[threshold_type]
            logger.info(f"Manual override cleared: {threshold_type.value}")
            return True
        return False

    def get_threshold(
        self,
        threshold_type: ThresholdType,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[float, ThresholdAdjustment]:
        """
        Get the current effective threshold value.

        Args:
            threshold_type: Threshold to retrieve
            context: Optional context for adaptive calculation

        Returns:
            Tuple of (threshold value, adjustment details)
        """
        context = context or {}
        now = context.get("timestamp", utc_now())

        config = self._configs.get(threshold_type)
        if not config:
            raise ValueError(f"Unknown threshold type: {threshold_type}")

        # Check for active manual override
        if threshold_type in self._manual_overrides:
            override = self._manual_overrides[threshold_type]
            if override.active_until is None or override.active_until > now:
                return override.adjusted_value, override
            else:
                # Override expired
                del self._manual_overrides[threshold_type]

        # Find applicable rules
        applicable_rules = [
            r
            for r in self._rules
            if threshold_type in r.threshold_types and r.evaluate(now, context)
        ]

        if not applicable_rules:
            # No adjustments, return base value
            adjustment = ThresholdAdjustment(
                threshold_type=threshold_type,
                base_value=config.base_value,
                adjusted_value=config.base_value,
                multiplier=1.0,
                reason=AdjustmentReason.SYSTEM_DEFAULT,
                explanation=f"Base {config.description.lower()}",
            )
            return config.base_value, adjustment

        # Apply highest priority rule
        best_rule = max(applicable_rules, key=lambda r: r.priority)
        adjusted_value = config.base_value * best_rule.multiplier

        # Clamp to valid range
        adjusted_value = max(
            config.min_value, min(config.max_value, adjusted_value)
        )

        adjustment = ThresholdAdjustment(
            threshold_type=threshold_type,
            base_value=config.base_value,
            adjusted_value=adjusted_value,
            multiplier=best_rule.multiplier,
            reason=best_rule.reason,
            explanation=f"{best_rule.name}: {best_rule.description}",
            priority=best_rule.priority,
        )

        self._current_adjustments[threshold_type] = adjustment
        return adjusted_value, adjustment

    def get_all_thresholds(
        self, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get all current threshold values with their adjustments.

        Args:
            context: Optional context for adaptive calculation

        Returns:
            Dictionary of all thresholds with details
        """
        result = {}
        for threshold_type in ThresholdType:
            value, adjustment = self.get_threshold(threshold_type, context)
            config = self._configs[threshold_type]
            result[threshold_type.value] = {
                "current_value": value,
                "base_value": config.base_value,
                "unit": config.unit,
                "description": config.description,
                "adjustment": adjustment.to_dict(),
            }
        return result

    def get_threshold_explanation(
        self,
        threshold_type: ThresholdType,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Get a human-readable explanation of the current threshold.

        Args:
            threshold_type: Threshold to explain
            context: Optional context

        Returns:
            Explanation string
        """
        value, adjustment = self.get_threshold(threshold_type, context)
        config = self._configs[threshold_type]

        if adjustment.multiplier == 1.0:
            return f"{config.description}: {value} {config.unit} (standard)"

        direction = "increased" if adjustment.multiplier > 1 else "decreased"
        percent = abs((adjustment.multiplier - 1) * 100)

        return (
            f"{config.description}: {value} {config.unit} "
            f"({direction} {percent:.0f}% due to {adjustment.reason.value})"
        )

    def check_threshold(
        self,
        threshold_type: ThresholdType,
        current_value: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Check if a value exceeds a threshold.

        Args:
            threshold_type: Threshold to check
            current_value: Current value to compare
            context: Optional context

        Returns:
            Check result with details
        """
        threshold_value, adjustment = self.get_threshold(
            threshold_type, context
        )
        config = self._configs[threshold_type]

        # For throughput, we check if value is BELOW threshold
        # For others, we check if value is ABOVE threshold
        is_throughput = "throughput" in threshold_type.value.lower()

        if is_throughput:
            exceeded = current_value < threshold_value
        else:
            exceeded = current_value > threshold_value

        return {
            "exceeded": exceeded,
            "current_value": current_value,
            "threshold_value": threshold_value,
            "unit": config.unit,
            "threshold_type": threshold_type.value,
            "adjustment": adjustment.to_dict(),
            "explanation": self.get_threshold_explanation(
                threshold_type, context
            ),
        }

    def add_time_window_rule(
        self,
        rule_id: str,
        name: str,
        threshold_types: List[ThresholdType],
        multiplier: float,
        start_time: time,
        end_time: time,
        days: Optional[List[int]] = None,
        reason: AdjustmentReason = AdjustmentReason.PEAK_HOURS,
    ) -> ThresholdRule:
        """
        Convenience method to add a time-window based rule.

        Args:
            rule_id: Unique rule identifier
            name: Human-readable name
            threshold_types: Thresholds this rule affects
            multiplier: Multiplier to apply
            start_time: Start time of window
            end_time: End time of window
            days: Days of week (0=Monday, 6=Sunday)
            reason: Reason for adjustment

        Returns:
            The created rule
        """
        window = TimeWindow(
            start=start_time,
            end=end_time,
            days=days or list(range(7)),
            label=f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}",
        )

        rule = ThresholdRule(
            id=rule_id,
            name=name,
            description=f"Time-based adjustment for {window.label}",
            threshold_types=threshold_types,
            multiplier=multiplier,
            condition=lambda dt, ctx: True,
            reason=reason,
            priority=15,
            time_windows=[window],
        )

        self.add_rule(rule)
        return rule

    def get_active_rules(
        self, context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of currently active rules.

        Args:
            context: Optional context

        Returns:
            List of active rule details
        """
        context = context or {}
        now = context.get("timestamp", utc_now())

        active = []
        for rule in self._rules:
            if rule.evaluate(now, context):
                active.append(
                    {
                        "id": rule.id,
                        "name": rule.name,
                        "description": rule.description,
                        "multiplier": rule.multiplier,
                        "reason": rule.reason.value,
                        "affected_thresholds": [
                            t.value for t in rule.threshold_types
                        ],
                    }
                )

        return active

    def learn_from_historical(
        self, session_id: str, lookback_hours: int = 168  # 1 week
    ) -> List[ThresholdRule]:
        """
        Analyze historical data to suggest threshold adjustments.

        Args:
            session_id: Session to analyze
            lookback_hours: Hours of history to analyze

        Returns:
            List of suggested rules based on patterns
        """
        if not self._conn:
            return []

        suggested_rules = []

        try:
            # Analyze hourly patterns
            cursor = self._conn.execute(
                """
                SELECT
                    strftime('%H', timestamp) as hour,
                    strftime('%w', timestamp) as day_of_week,
                    COUNT(*) as events,
                    AVG(CASE WHEN stage = 'QUEUE_JOIN' THEN 1 ELSE 0 END) * 100 as join_rate
                FROM events
                WHERE session_id = ?
                    AND datetime(timestamp) > datetime('now', '-' || ? || ' hours')
                GROUP BY strftime('%H', timestamp), strftime('%w', timestamp)
                HAVING COUNT(*) > 5
            """,
                (session_id, lookback_hours),
            )

            hourly_data = cursor.fetchall()

            # Find consistent peak hours
            if hourly_data:
                avg_events = sum(r["events"] for r in hourly_data) / len(
                    hourly_data
                )
                peak_hours = [
                    r for r in hourly_data if r["events"] > avg_events * 1.5
                ]

                if len(peak_hours) >= 3:
                    # Create rule for identified peak hours
                    peak_hour_times = list(
                        set(int(r["hour"]) for r in peak_hours)
                    )
                    peak_hour_times.sort()

                    # Group consecutive hours
                    groups = []
                    current_group = [peak_hour_times[0]]
                    for h in peak_hour_times[1:]:
                        if h == current_group[-1] + 1:
                            current_group.append(h)
                        else:
                            if len(current_group) >= 2:
                                groups.append(current_group)
                            current_group = [h]
                    if len(current_group) >= 2:
                        groups.append(current_group)

                    for i, group in enumerate(groups):
                        rule = ThresholdRule(
                            id=f"learned_peak_{i}",
                            name=f"Learned Peak Period {i+1}",
                            description=f"High demand period identified from historical data ({group[0]:02d}:00-{group[-1]:02d}:59)",
                            threshold_types=[
                                ThresholdType.QUEUE_WARNING,
                                ThresholdType.QUEUE_CRITICAL,
                                ThresholdType.WAIT_WARNING,
                                ThresholdType.WAIT_CRITICAL,
                            ],
                            multiplier=1.2,
                            condition=lambda dt, ctx: True,
                            reason=AdjustmentReason.HISTORICAL_PATTERN,
                            priority=5,
                            time_windows=[
                                TimeWindow(
                                    time(group[0], 0),
                                    time(group[-1], 59),
                                    label=f"Historical peak {group[0]:02d}:00-{group[-1]:02d}:59",
                                )
                            ],
                        )
                        suggested_rules.append(rule)

        except Exception as e:
            logger.error(f"Error learning from historical data: {e}")

        return suggested_rules

    def apply_learned_rules(self, rules: List[ThresholdRule]) -> int:
        """Apply a list of learned rules"""
        added = 0
        for rule in rules:
            self.add_rule(rule)
            added += 1
        return added


# =============================================================================
# Convenience Functions for Common Threshold Types
# =============================================================================


class ThresholdChecker:
    """Convenience class for checking multiple thresholds"""

    def __init__(self, manager: AdaptiveThresholdManager):
        self._manager = manager

    def check_queue(
        self, queue_size: int, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Check queue-related thresholds"""
        warning = self._manager.check_threshold(
            ThresholdType.QUEUE_WARNING, queue_size, context
        )
        critical = self._manager.check_threshold(
            ThresholdType.QUEUE_CRITICAL, queue_size, context
        )

        return {
            "queue_size": queue_size,
            "warning": warning,
            "critical": critical,
            "status": (
                "critical"
                if critical["exceeded"]
                else ("warning" if warning["exceeded"] else "ok")
            ),
        }

    def check_wait_time(
        self, wait_minutes: float, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Check wait time thresholds"""
        warning = self._manager.check_threshold(
            ThresholdType.WAIT_WARNING, wait_minutes, context
        )
        critical = self._manager.check_threshold(
            ThresholdType.WAIT_CRITICAL, wait_minutes, context
        )

        return {
            "wait_minutes": wait_minutes,
            "warning": warning,
            "critical": critical,
            "status": (
                "critical"
                if critical["exceeded"]
                else ("warning" if warning["exceeded"] else "ok")
            ),
        }

    def check_all(
        self,
        metrics: Dict[str, float],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Check all relevant thresholds against provided metrics.

        Args:
            metrics: Dictionary with keys like "queue_size", "wait_time", "throughput"
            context: Optional context

        Returns:
            Comprehensive threshold check results
        """
        results = {}

        if "queue_size" in metrics:
            results["queue"] = self.check_queue(metrics["queue_size"], context)

        if "wait_time" in metrics:
            results["wait_time"] = self.check_wait_time(
                metrics["wait_time"], context
            )

        if "throughput" in metrics:
            warning = self._manager.check_threshold(
                ThresholdType.THROUGHPUT_WARNING,
                metrics["throughput"],
                context,
            )
            critical = self._manager.check_threshold(
                ThresholdType.THROUGHPUT_CRITICAL,
                metrics["throughput"],
                context,
            )
            results["throughput"] = {
                "throughput": metrics["throughput"],
                "warning": warning,
                "critical": critical,
                "status": (
                    "critical"
                    if critical["exceeded"]
                    else ("warning" if warning["exceeded"] else "ok")
                ),
            }

        if "inactivity_minutes" in metrics:
            warning = self._manager.check_threshold(
                ThresholdType.INACTIVITY_WARNING,
                metrics["inactivity_minutes"],
                context,
            )
            critical = self._manager.check_threshold(
                ThresholdType.INACTIVITY_CRITICAL,
                metrics["inactivity_minutes"],
                context,
            )
            results["inactivity"] = {
                "inactivity_minutes": metrics["inactivity_minutes"],
                "warning": warning,
                "critical": critical,
                "status": (
                    "critical"
                    if critical["exceeded"]
                    else ("warning" if warning["exceeded"] else "ok")
                ),
            }

        # Calculate overall status
        statuses = [r.get("status", "ok") for r in results.values()]
        if "critical" in statuses:
            overall = "critical"
        elif "warning" in statuses:
            overall = "warning"
        else:
            overall = "ok"

        results["overall_status"] = overall
        return results


# =============================================================================
# Global Instance
# =============================================================================

_threshold_manager: Optional[AdaptiveThresholdManager] = None


def get_threshold_manager(
    conn: Optional[sqlite3.Connection] = None,
) -> AdaptiveThresholdManager:
    """Get or create the global threshold manager"""
    global _threshold_manager
    if _threshold_manager is None:
        _threshold_manager = AdaptiveThresholdManager(conn)
    return _threshold_manager


def get_threshold_checker(
    conn: Optional[sqlite3.Connection] = None,
) -> ThresholdChecker:
    """Get a threshold checker using the global manager"""
    return ThresholdChecker(get_threshold_manager(conn))

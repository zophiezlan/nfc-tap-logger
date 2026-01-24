"""
Festival scenario configurations based on real NSW deployments
Each scenario represents actual or projected festival drug checking operations
"""

FESTIVAL_SCENARIOS = {
    'htid': {
        'name': 'HTID (Hardstyle Til I Die)',
        'description': 'Single day hardstyle festival - Manageable demand',
        'emoji': '🎵',
        'duration_hours': 6,
        'days': 1,
        'session_id': 'htid-2026-demo',

        # Staffing
        'peer_workers': 6,
        'chemists': 6,

        # Actual results
        'total_samples': 110,
        'total_groups': 70,
        'samples_per_group_avg': 1.6,  # Mix of 1-3 samples

        # Service times
        'peer_intake_min': 5,
        'testing_min': 8,
        'results_chat_min': 10,
        'results_chat_variance': 'medium',  # Some go 30+ mins

        # Demand pattern
        'demand_level': 'moderate',
        'arrival_pattern': {
            'hour_0_1': 0.3,   # Quiet start
            'hour_1_2': 1.5,   # Building
            'hour_2_3': 2.5,   # Peak
            'hour_3_4': 2.5,   # Peak continues
            'hour_4_5': 0.6,   # Dropping
            'hour_5_6': 0.2,   # Almost done
        },

        # Queue dynamics
        'max_queue_observed': 15,
        'avg_wait_time_min': 10,
        'max_wait_time_min': 30,
        'abandonment_rate': 0.02,  # Very low

        # Capacity
        'throughput_per_hour': 12,  # 70 groups / 6 hours
        'service_time_total_min': 23,

        # Outcomes
        'outcome': 'success',
        'outcome_description': 'Service met demand. Manageable queues. Good participant experience.',
        'lesson': 'Optimal staffing for moderate demand festival',

        # Alert thresholds
        'queue_warning': 10,
        'queue_critical': 15,
        'wait_warning_min': 30,
        'wait_critical_min': 60,
        'stuck_threshold_min': 45,
    },

    'lost_paradise_actual': {
        'name': 'Lost Paradise (Actual Deployment)',
        'description': '2-day festival - OVERWHELMED capacity, 3hr waits, many turned away',
        'emoji': '🌴',
        'duration_hours': 6,
        'days': 2,
        'session_id': 'lost-paradise-actual-2026-demo',

        # Staffing (SAME as HTID but WAY more demand!)
        'peer_workers': 6,
        'chemists': 6,

        # Actual results
        'total_samples': 300,  # Over 2 days
        'total_groups': 150,   # 2 samples/group cap, max 2 people/group
        'samples_per_group_avg': 2.0,  # Capped at 2, 80% brought 2, 20% brought 1

        # Service times (SAME as HTID but under extreme pressure)
        'peer_intake_min': 5,
        'testing_min': 8,
        'results_chat_min': 8,  # Shorter - had to rush due to queue
        'results_chat_variance': 'low',  # No time for long chats when queue is 3 hours

        # Demand pattern (CONSTANT OVERLOAD)
        'demand_level': 'critical_overload',
        'arrival_pattern': {
            # Queue out the door from open to close, both days
            'hour_0_1': 3.5,   # Line before opening
            'hour_1_2': 3.5,   # Constant
            'hour_2_3': 3.5,   # Constant
            'hour_3_4': 3.5,   # Constant
            'hour_4_5': 3.5,   # Constant
            'hour_5_6': 3.0,   # Slightly drops as people give up
        },

        # Queue dynamics (CRITICAL)
        'max_queue_observed': 60,  # Estimate - line out the door
        'avg_wait_time_min': 120,  # 2 hours average
        'max_wait_time_min': 180,  # 3 hours peak!
        'abandonment_rate': 0.25,  # 25% left due to wait - MANY people turned away

        # Capacity (same throughput but INSUFFICIENT)
        'throughput_per_hour': 12,  # Same as HTID
        'service_time_total_min': 21,  # Slightly faster - rushing

        # Outcomes
        'outcome': 'critical_understaffed',
        'outcome_description': 'Severe understaffing. 3hr waits. Many participants turned away. Staff burnout.',
        'lesson': 'Demonstrates urgent need for scaled resources at multi-day festivals',

        # Alert thresholds (adjusted for crisis mode)
        'queue_warning': 30,
        'queue_critical': 50,
        'wait_warning_min': 90,
        'wait_critical_min': 150,
        'stuck_threshold_min': 45,
    },

    'lost_paradise_ideal': {
        'name': 'Lost Paradise (Ideal Staffing)',
        'description': '2-day festival - PROPER resourcing, manageable queues, no one turned away',
        'emoji': '🌟',
        'duration_hours': 6,
        'days': 2,
        'session_id': 'lost-paradise-ideal-2026-demo',

        # Staffing (DOUBLED!)
        'peer_workers': 12,
        'chemists': 12,

        # Projected results (could handle even MORE)
        'total_samples': 500,  # Could test more with double staff
        'total_groups': 250,   # Could handle 4x HTID
        'samples_per_group_avg': 2.0,

        # Service times (BETTER - no rushing)
        'peer_intake_min': 5,
        'testing_min': 8,
        'results_chat_min': 10,  # Can take proper time
        'results_chat_variance': 'medium',  # Time for quality conversations

        # Demand pattern (SAME high demand but can HANDLE it)
        'demand_level': 'high_manageable',
        'arrival_pattern': {
            # Same arrivals as actual, but now manageable
            'hour_0_1': 3.5,
            'hour_1_2': 3.5,
            'hour_2_3': 3.5,
            'hour_3_4': 3.5,
            'hour_4_5': 3.5,
            'hour_5_6': 3.0,
        },

        # Queue dynamics (IMPROVED!)
        'max_queue_observed': 20,  # Much better!
        'avg_wait_time_min': 25,   # Under 30 min
        'max_wait_time_min': 45,   # Peak still reasonable
        'abandonment_rate': 0.03,  # Minimal - only people in a rush

        # Capacity (DOUBLED)
        'throughput_per_hour': 24,  # Double the throughput
        'service_time_total_min': 23,  # Back to quality service

        # Outcomes
        'outcome': 'success_scaled',
        'outcome_description': 'Proper resourcing meets demand. <30min waits. Quality conversations. Happy participants.',
        'lesson': 'Shows cost-benefit of proper staffing investment for multi-day festivals',

        # Alert thresholds
        'queue_warning': 15,
        'queue_critical': 25,
        'wait_warning_min': 30,
        'wait_critical_min': 60,
        'stuck_threshold_min': 45,
    },
}


def get_scenario_config(scenario_name: str) -> dict:
    """Get configuration for a specific festival scenario"""
    if scenario_name not in FESTIVAL_SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_name}. Available: {list(FESTIVAL_SCENARIOS.keys())}")

    return FESTIVAL_SCENARIOS[scenario_name]


def get_scenario_summary(scenario_name: str) -> dict:
    """Get summary info for display"""
    scenario = FESTIVAL_SCENARIOS[scenario_name]

    return {
        'name': scenario['name'],
        'description': scenario['description'],
        'emoji': scenario['emoji'],
        'staff': f"{scenario['peer_workers']} peers, {scenario['chemists']} chemists",
        'duration': f"{scenario['days']} day{'s' if scenario['days'] > 1 else ''}, {scenario['duration_hours']}hr/day",
        'served': f"{scenario['total_groups']} groups, {scenario['total_samples']} samples",
        'outcome': scenario['outcome_description'],
        'max_wait': f"{scenario['max_wait_time_min']} min",
        'abandonment': f"{int(scenario['abandonment_rate'] * 100)}%"
    }


def list_scenarios() -> list:
    """List all available scenarios"""
    return [
        {
            'id': key,
            'name': scenario['name'],
            'emoji': scenario['emoji'],
            'description': scenario['description'],
            'outcome': scenario['outcome']
        }
        for key, scenario in FESTIVAL_SCENARIOS.items()
    ]

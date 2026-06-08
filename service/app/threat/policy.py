"""Default agency threat assessment policy profiles."""

from app.threat.schemas import PolicyIndicator, ThreatIndicatorCategory, ThreatPolicyProfile

DEFAULT_INDICATORS: list[PolicyIndicator] = [
    PolicyIndicator(
        id="assault_on_officer",
        label="Prior assault on peace officer",
        category=ThreatIndicatorCategory.PERSON,
        weight=4.0,
        mandatory_supervisor_notify=True,
    ),
    PolicyIndicator(
        id="firearm_recovery",
        label="Prior firearm recovery during contact",
        category=ThreatIndicatorCategory.PERSON,
        weight=3.5,
    ),
    PolicyIndicator(
        id="active_warrant_violent",
        label="Active violent felony warrant",
        category=ThreatIndicatorCategory.PERSON,
        weight=4.5,
        mandatory_supervisor_notify=True,
    ),
    PolicyIndicator(
        id="protective_order_violation",
        label="Active protective order violation history",
        category=ThreatIndicatorCategory.PERSON,
        weight=3.0,
    ),
    PolicyIndicator(
        id="weapons_incidents_location",
        label="Weapons-related incidents at location",
        category=ThreatIndicatorCategory.LOCATION,
        weight=2.5,
    ),
    PolicyIndicator(
        id="repeat_dv_location",
        label="Repeat domestic violence calls at location",
        category=ThreatIndicatorCategory.LOCATION,
        weight=2.0,
    ),
    PolicyIndicator(
        id="stolen_vehicle",
        label="Stolen vehicle entry",
        category=ThreatIndicatorCategory.VEHICLE,
        weight=3.0,
    ),
    PolicyIndicator(
        id="prior_pursuit",
        label="Prior pursuit involving vehicle",
        category=ThreatIndicatorCategory.VEHICLE,
        weight=2.5,
    ),
    PolicyIndicator(
        id="weapons_on_incident",
        label="Weapons reported on current incident",
        category=ThreatIndicatorCategory.INCIDENT,
        weight=3.5,
    ),
    PolicyIndicator(
        id="multiple_involved_persons",
        label="Multiple involved persons on incident",
        category=ThreatIndicatorCategory.INCIDENT,
        weight=1.5,
    ),
]

DEFAULT_POLICY = ThreatPolicyProfile(
    policy_id="default-officer-safety",
    agency_id="*",
    name="Default Officer Safety Assessment Policy",
    version=1,
    indicators=DEFAULT_INDICATORS,
    advisory_threshold=3.0,
    elevated_threshold=6.0,
    critical_threshold=9.0,
    officer_warning_template="Officer Safety Advisory: {factors}",
)

_POLICY_STORE: dict[str, ThreatPolicyProfile] = {"default-officer-safety": DEFAULT_POLICY}


def get_policy(policy_id: str, agency_id: str) -> ThreatPolicyProfile:
    key = f"{agency_id}:{policy_id}"
    if key in _POLICY_STORE:
        return _POLICY_STORE[key]
    if policy_id in _POLICY_STORE:
        return _POLICY_STORE[policy_id]
    return DEFAULT_POLICY


def upsert_policy(profile: ThreatPolicyProfile) -> ThreatPolicyProfile:
    key = f"{profile.agency_id}:{profile.policy_id}"
    _POLICY_STORE[key] = profile
    return profile


def list_policies(agency_id: str | None = None) -> list[ThreatPolicyProfile]:
    if not agency_id:
        return list(_POLICY_STORE.values())
    return [p for p in _POLICY_STORE.values() if p.agency_id in ("*", agency_id)]

"""
Project: Zero-Trust Network Access (ZTNA) Demo
Name: Payal Jangid
Program: Cybersecurity Bootcamp
Date: 22-10-2026

IMPORTANT:
This is a local educational simulation of ZTNA policy enforcement. It does NOT
create a real Cloudflare Tunnel, configure Cloudflare Access, or enforce real
MFA. Use the Cloudflare dashboard and official cloudflared tooling for those
deployment steps. This demo shows the access-decision logic safely in Python.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import FrozenSet


@dataclass(frozen=True)
class AccessRequest:
    user_email: str
    mfa_verified: bool
    device_compliant: bool
    requested_resource: str


@dataclass(frozen=True)
class AccessDecision:
    allowed: bool
    reasons: tuple[str, ...]
    timestamp_utc: str


class ZeroTrustPolicy:
    """Default-deny policy: grant access only when every rule passes."""

    def __init__(
        self,
        allowed_users: FrozenSet[str],
        protected_resources: FrozenSet[str],
        require_mfa: bool = True,
        require_compliant_device: bool = True,
    ) -> None:
        self.allowed_users = frozenset(email.lower() for email in allowed_users)
        self.protected_resources = frozenset(protected_resources)
        self.require_mfa = require_mfa
        self.require_compliant_device = require_compliant_device

    def evaluate(self, request: AccessRequest) -> AccessDecision:
        reasons = []

        if request.user_email.lower() not in self.allowed_users:
            reasons.append("User is not on the authorized-user allowlist.")

        if request.requested_resource not in self.protected_resources:
            reasons.append("Requested resource is not an approved protected resource.")

        if self.require_mfa and not request.mfa_verified:
            reasons.append("Multi-factor authentication has not been verified.")

        if self.require_compliant_device and not request.device_compliant:
            reasons.append("Device does not meet the compliance requirement.")

        allowed = len(reasons) == 0
        if allowed:
            reasons.append("All configured Zero-Trust checks passed.")

        return AccessDecision(
            allowed=allowed,
            reasons=tuple(reasons),
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
        )


def print_decision(label: str, request: AccessRequest, policy: ZeroTrustPolicy) -> None:
    decision = policy.evaluate(request)
    status = "ALLOW" if decision.allowed else "DENY"
    print(f"\n[{label}] {status}")
    print(f"User: {request.user_email}")
    print(f"Resource: {request.requested_resource}")
    for reason in decision.reasons:
        print(f" - {reason}")
    print(f"Evaluated (UTC): {decision.timestamp_utc}")


def run_demo() -> None:
    # Replace these sample values with non-sensitive test identities/resources.
    policy = ZeroTrustPolicy(
        allowed_users=frozenset({"admin@example.com"}),
        protected_resources=frozenset({"internal-admin-console"}),
        require_mfa=True,
        require_compliant_device=True,
    )

    test_requests = [
        (
            "Authorized admin, MFA verified, compliant device",
            AccessRequest(
                user_email="admin@example.com",
                mfa_verified=True,
                device_compliant=True,
                requested_resource="internal-admin-console",
            ),
        ),
        (
            "MFA missing",
            AccessRequest(
                user_email="admin@example.com",
                mfa_verified=False,
                device_compliant=True,
                requested_resource="internal-admin-console",
            ),
        ),
        (
            "Unauthorized user",
            AccessRequest(
                user_email="visitor@example.com",
                mfa_verified=True,
                device_compliant=True,
                requested_resource="internal-admin-console",
            ),
        ),
        (
            "Unapproved resource",
            AccessRequest(
                user_email="admin@example.com",
                mfa_verified=True,
                device_compliant=True,
                requested_resource="public-dashboard",
            ),
        ),
        (
            "Non-compliant device",
            AccessRequest(
                user_email="admin@example.com",
                mfa_verified=True,
                device_compliant=False,
                requested_resource="internal-admin-console",
            ),
        ),
    ]

    for label, request in test_requests:
        print_decision(label, request, policy)


if __name__ == "__main__":
    run_demo()

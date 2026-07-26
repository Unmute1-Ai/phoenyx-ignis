from ignis.policy import Policy


def test_safe_policy_requires_approval_and_uefi():
    policy = Policy.safe_default()
    denied = policy.evaluate("repair.windows.bootmanager_entry", {"uefi": False})
    assert not denied.allowed
    assert "UEFI firmware is required" in denied.reasons
    assert "explicit operator approval is required" in denied.reasons


def test_safe_policy_allows_approved_uefi_repair():
    decision = Policy.safe_default().evaluate(
        "repair.windows.bootmanager_entry", {"uefi": True}, approved=True
    )
    assert decision.allowed


def test_policy_denies_unknown_primitive():
    decision = Policy.safe_default().evaluate("repair.erase.everything", {}, approved=True)
    assert not decision.allowed
    assert decision.reasons == ("primitive is not allowlisted",)

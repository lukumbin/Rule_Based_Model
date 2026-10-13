from __future__ import annotations  # This allows for forward references in type hints, enabling the use of class names before they are fully defined.

from dataclasses import dataclass # Allows for the creation of data classes 
from typing import Callable, Dict, List, Tuple # type hints, help explain what the code expects

import pandas as pd  # import pandas library for data manipulation and analysis


@dataclass(frozen=True)  #template for one scoring rule, can't be changed whilst program is running
class Rule:
    rule_name: str
    points: int
    reason: str
    condition: Callable[[pd.Series], bool] # checks whether the rule condition is met


def get_rules() -> List[Rule]:
    """
    Transparent business-inspired rules for a rule based scoring model prototype.

    These thresholds are for demonstration purposes only.
    In real business implementation, the rules must be validated.
    """
    return [    
        Rule(
            rule_name="VERY_HIGH_CLAIM_AMOUNT",
            points=30,
            reason="Very high claimed amount",
            condition=lambda r: r["ClaimedAmount"] > 150_000,
        ),
        Rule(
            rule_name="HIGH_CLAIM_AMOUNT",
            points=20,
            reason="High claimed amount",
            condition=lambda r: 75_000 < r["ClaimedAmount"] <= 150_000,
        ),
        Rule(
            rule_name="NEW_POLICY",
            points=20,
            reason="Policy is younger than 90 days",
            condition=lambda r: r["PolicyAgeDays"] < 90,
        ),
        Rule(
            rule_name="POOR_PAYMENT_HISTORY",
            points=15,
            reason="Poor payment history score",
            condition=lambda r: r["PaymentHistoryScore"] < 60,
        ),
        Rule(
            rule_name="MULTIPLE_PREVIOUS_CLAIMS",
            points=15,
            reason="Multiple previous claims",
            condition=lambda r: r["PreviousClaimsCount"] >= 2,
        ),
        Rule(
            rule_name="LATE_REPORTING",
            points=10,
            reason="Claim reported more than 7 days after incident",
            condition=lambda r: r["ReportedDelayDays"] > 7,
        ),
        Rule(
            rule_name="EVIDENCE_INQUIRY",
            points=20,
            reason="Evidence inquiry required",
            condition=lambda r: r["EvidenceInquiryFlag"] == 1,
        ),
        Rule(
            rule_name="RED_FLAG_REVIEW",
            points=25,
            reason="Red flag review triggered",
            condition=lambda r: r["RedFlagReviewFlag"] == 1,
        ),
        Rule(
            rule_name="MANAGER_FOLLOW_UP",
            points=15,
            reason="Manager follow-up required",
            condition=lambda r: r["ManagerFollowUpFlag"] == 1,
        ),
        Rule(
            rule_name="WRITE_OFF",
            points=25,
            reason="Possible write-off",
            condition=lambda r: r["WriteOffFlag"] == 1,
        ),
        Rule(
            rule_name="LONG_DESKTOP_QUEUE",
            points=10,
            reason="Long desktop queue time",
            condition=lambda r: r["DesktopQueueDays"] > 3,
        ),
        Rule(
            rule_name="YOUNG_DRIVER_HIGH_VALUE",
            points=10,
            reason="Young driver with high claimed amount",
            condition=lambda r: r["DriverAge"] < 25 and r["ClaimedAmount"] > 50_000,
        ),
        Rule(
            rule_name="OLDER_VEHICLE_HIGH_VALUE",
            points=10,
            reason="Older vehicle with high claimed amount",
            condition=lambda r: r["VehicleAge"] >= 10 and r["ClaimedAmount"] > 60_000,
        ),
    ]


def classify_score(score: int) -> Tuple[str, str]:
    """
    Converts numeric score into a business-friendly risk band and action.
    """
    if score >= 60:
        return "High", "Senior review"
    if score >= 30:
        return "Medium", "Monitor"
    return "Low", "Fast-track"


def score_claim(row: pd.Series) -> Dict[str, object]:
    """
    Scores one claim using the rules above.
    """
    score = 0
    triggered_rules: List[str] = []
    reasons: List[str] = []

    for rule in get_rules():
        if rule.condition(row):
            score += rule.points
            triggered_rules.append(rule.rule_name)
            reasons.append(rule.reason)

    risk_band, recommended_action = classify_score(score)

    return {
        "RiskScore": score,
        "RiskBand": risk_band,
        "RecommendedAction": recommended_action,
        "PrimaryRiskReason": reasons[0] if reasons else "Low risk profile",
        "SecondaryRiskReason": reasons[1] if len(reasons) > 1 else "",
        "TriggeredRules": "; ".join(triggered_rules) if triggered_rules else "NONE",
        "RiskReasons": "; ".join(reasons) if reasons else "Low risk profile",
        "FastTrackEligibleFlag": int(risk_band == "Low"),
        "SeniorReviewFlag": int(risk_band == "High"),
        "SlaBreachRiskFlag": int(score >= 50 or row["DesktopQueueDays"] > 4 or row["TATBreachFlag"] == 1),
    }


def score_claims(df: pd.DataFrame) -> pd.DataFrame:
    """
    Scores all claims and appends score/action columns to the original dataset.
    """
    scored_columns = df.apply(score_claim, axis=1, result_type="expand")
    return pd.concat([df.copy(), scored_columns], axis=1)


def build_risk_summary(scored_df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a summary by RiskBand and RecommendedAction for Power BI.
    """
    return (
        scored_df.groupby(["RiskBand", "RecommendedAction"], as_index=False)
        .agg(
            Claims=("ClaimId", "count"),
            AverageRiskScore=("RiskScore", "mean"),
            TotalClaimedAmount=("ClaimedAmount", "sum"),
            AverageClaimedAmount=("ClaimedAmount", "mean"),
            FastTrackEligible=("FastTrackEligibleFlag", "sum"),
            SeniorReview=("SeniorReviewFlag", "sum"),
            SlaBreachRisk=("SlaBreachRiskFlag", "sum"),
        )
        .sort_values("AverageRiskScore", ascending=False)
    )


def build_rule_impact_summary(scored_df: pd.DataFrame) -> pd.DataFrame:
    """
    Explodes TriggeredRules and summarizes how often each rule fired.
    """
    rows = []

    for _, row in scored_df.iterrows():
        rules = [rule for rule in str(row["TriggeredRules"]).split("; ") if rule and rule != "NONE"]

        for rule in rules:
            rows.append(
                {
                    "RuleName": rule,
                    "ClaimId": row["ClaimId"],
                    "RiskScore": row["RiskScore"],
                    "RiskBand": row["RiskBand"],
                    "ClaimedAmount": row["ClaimedAmount"],
                }
            )

    if not rows:
        return pd.DataFrame(
            columns=[
                "RuleName",
                "ClaimsTriggered",
                "AverageRiskScore",
                "TotalClaimedAmount",
                "HighRiskClaims",
            ]
        )

    exploded = pd.DataFrame(rows)

    return (
        exploded.groupby("RuleName", as_index=False)
        .agg(
            ClaimsTriggered=("ClaimId", "nunique"),
            AverageRiskScore=("RiskScore", "mean"),
            TotalClaimedAmount=("ClaimedAmount", "sum"),
            HighRiskClaims=("RiskBand", lambda s: (s == "High").sum()),
        )
        .sort_values(["ClaimsTriggered", "AverageRiskScore"], ascending=[False, False])
    )

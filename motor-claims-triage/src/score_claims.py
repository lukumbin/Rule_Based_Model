from pathlib import Path 

import pandas as pd

from rules_engine import build_rule_impact_summary, score_claims


PROJECT_ROOT = Path(__file__).resolve().parents[1]  # finds the main project folder 

INPUT_PATH = PROJECT_ROOT / "data" / "sample" / "motor_claims_demo.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

INPUT_SHEET = "Claims"


def main() -> None:   #type hint: main function that runs the scoring engine and generates outputs
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True) 

    # Read the input Excel file
    claims = pd.read_excel(INPUT_PATH, sheet_name=INPUT_SHEET)

    # Apply the rule-based scoring engine
    scored_claims = score_claims(claims)

    # Create summary output
    risk_summary = (
        scored_claims.groupby(["RiskBand", "RecommendedAction"], as_index=False)
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

    rule_impact_summary = build_rule_impact_summary(scored_claims)

    # Save outputs 
    scored_claims.to_excel(OUTPUT_DIR / "scored_claims.xlsx", index=False)
    risk_summary.to_excel(OUTPUT_DIR / "risk_summary.xlsx", index=False)
    rule_impact_summary.to_excel(OUTPUT_DIR / "rule_impact_summary.xlsx", index=False)

    # Print output to terminal
    print("\n==============================")
    print("MOTOR CLAIMS TRIAGE COMPLETE")
    print("==============================\n")

    print("Risk Summary:")
    print(risk_summary.to_string(index=False)) # converts dataframe into readable text 

    print("\nTop 10 Highest Risk Claims:")
    top_claims = scored_claims.sort_values("RiskScore", ascending=False).head(10) #sort by risk score and return top 10 claims 

    print(
        top_claims[
            [
                "ClaimId",
                "ClaimType",
                "ClaimedAmount",
                "PolicyAgeDays",
                "PaymentHistoryScore",
                "PreviousClaimsCount",
                "RiskScore",
                "RiskBand",
                "RecommendedAction",
                "PrimaryRiskReason",
                "TriggeredRules",
            ]
        ].to_string(index=False) # converts dataframe into readable text
    )

    print("\nRule Impact Summary:")
    print(rule_impact_summary.to_string(index=False))

    print("\nOutput files created:")
    print(f"- {OUTPUT_DIR / 'scored_claims.xlsx'}")
    print(f"- {OUTPUT_DIR / 'risk_summary.xlsx'}")
    print(f"- {OUTPUT_DIR / 'rule_impact_summary.xlsx'}")


if __name__ == "__main__":
    main()
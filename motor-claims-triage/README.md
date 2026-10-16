# Rule-Based Motor Claims Triage Engine

## What this project does

This is a personal portfolio prototype for short-term motor insurance.

It reads a demo Excel file of motor claims, applies transparent business rules, and creates scored Excel outputs for Power BI.

The project does **not** use real company, customer, policy, or claim data.

## Flow

```text
Excel demo claims file
        ↓
Python rules engine
        ↓
Scored outputs
        
```

## Files

```text
data/sample/motor_claims_demo.xlsx      # Input Excel file
src/rules_engine.py                     # Risk scoring logic
src/score_claims_excel.py               # Script that reads Excel and creates outputs
outputs/scored_claims.xlsx              # Created after running Python
outputs/risk_summary.xlsx               # Created after running Python
outputs/rule_impact_summary.xlsx        # Created after running Python
```

## How to run

Open the project folder in VS Code.

Then run these commands one at a time:

```powershell
python -m venv .venv
```

```powershell
.venv\Scripts\activate
```

```powershell
pip install -r requirements.txt
```

```powershell
python src/score_claims_excel.py
```

## What Python creates

After running the scoring script, the `outputs` folder will contain:

| Output file | Purpose |
|---|---|
| `scored_claims.xlsx` | Claim-level risk scores and recommended actions |
| `risk_summary.xlsx` | Summary by risk band |
| `rule_impact_summary.xlsx` | Summary of which rules triggered most often |

## Risk score logic

Each claim starts at 0 points. Rules add points based on risk indicators.

Example:

| Rule | Points |
|---|---:|
| Very high claimed amount | 30 |
| High claimed amount | 20 |
| New policy | 20 |
| Poor payment history | 15 |
| Multiple previous claims | 15 |
| Late reporting | 10 |
| Evidence inquiry | 20 |
| Red flag review | 25 |
| Manager follow-up | 15 |
| Possible write-off | 25 |
| Long desktop queue | 10 |

## Risk bands

| Score | Band | Recommended action |
|---:|---|---|
| 0 - 29 | Low | Fast-track |
| 30 - 59 | Medium | Monitor |
| 60+ | High | Senior review |



In a real business implementation, the Excel input could be replaced with approved SQL claims data. The same scoring logic could then feed a Power BI dashboard through a scheduled process.

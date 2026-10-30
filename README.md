# Ethical AI Systems — Companion Toolkit

[![tests](https://github.com/compassionate-ai-lab/ethical-ai-systems/actions/workflows/tests.yml/badge.svg)](https://github.com/compassionate-ai-lab/ethical-ai-systems/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![License: MIT](https://img.shields.io/badge/license-MIT-green) ![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

<img src="images/ethical-ai-systems-cover.jpg" alt="Ethical AI Systems book cover" width="220" align="right">

Companion code and worksheets for **[Ethical AI Systems: Frameworks, Principles, and Advanced Practices for the Age of Autonomous Intelligence](https://amitray.com/ethical-ai-systems-ebook/)** by **Dr. Sri Amit Ray** (Compassionate AI Lab, Revised Expanded Edition, 2026, ISBN 978-81-69641-39-5).

> Power to act must remain connected to responsibility, care and human freedom. Rights and severe-harm limits decide what is admissible; benefit decides only among the actions that remain.

**Get the full-colour eBook:** https://amitray.com/ethical-ai-systems-ebook/

## What is here

| File | What it does |
|---|---|
| `ethical_ai_toolkit.py` | Ten-index scorecard (Chapter 5, Appendix A), autonomy ceiling matrix (Chapter 7, Appendix C), cumulative budget envelope, fairness metrics, action record. Standard library only. |
| `test_ethical_ai_toolkit.py` | 10 regression tests: the 66.64 score, mandatory gates, approved N/A, invalid input, monotone autonomy limits, cumulative spending, duplicate action IDs, decimal money, revocation, subgroup rates, calibration bins. |
| `forms/` | The Forms Workbook: 11 worksheets (colour and black-and-white printable PDFs, editable DOCX, Markdown source). |

## Quick start

```bash
git clone https://github.com/compassionate-ai-lab/ethical-ai-systems.git
cd ethical-ai-systems
python ethical_ai_toolkit.py                       # self-tests
python -m unittest -v test_ethical_ai_toolkit.py   # regression tests
```

```python
from ethical_ai_toolkit import Assessment, Envelope, allowed_rung

scores = {"cage": 55, "traps": 71, "bias": 62, "hostility": 83, "diversity": 58,
          "collection": 74, "transparency": 66, "anonymisation": 80,
          "augmentation": 70, "oversight": 52}
print(Assessment(scores).summary())   # HOLD: composite 66.64
print(allowed_rung(2, 0))             # 1 -> high impact: approve to act
```

## The book in brief

- **Part I, Foundations:** the ethical mandate, frameworks and instruments, the service pyramid.
- **Part II, Data and Models:** data ethics; bias, fairness and the ten ethical AI indexes; transparency, explainability and traceability.
- **Part III, Systems that Act:** agentic accountability, consent and oversight; safety, security and containment; human–robot interaction.
- **Part IV, Domains and Institutions:** health and drug design; ethics under pressure; governance, measurement and the road ahead.
- **Appendices:** scoring rubric, service pyramid checklist, autonomy ladder and oversight matrix, audit and red-team protocol, the companion toolkit.

## Boundary

Educational reference code. It is not a production authorisation service, a compliance certificate, concurrent transaction processing or cryptographic logging.

## Verifying the release

The book prints the SHA-256 of the companion package `Ethical_AI_Systems_Companion_Toolkit_v1.0.0.zip` on its copyright page and in Appendix E:

```
e1b62ee1c3ba5f679f96424f88b0d45afdd0437bb0c6cd26654908fe86d43d6e
```

## Related

- Compassionate AI Lab: https://amitray.com/compassionate-ai-lab/
- Other companion repositories: https://github.com/compassionate-ai-lab

## Licence and citation

Code: MIT License (see `LICENSE`). Worksheets: may be reproduced by purchasers for their own use and within their organisations. Please cite the book (see `CITATION.cff`).

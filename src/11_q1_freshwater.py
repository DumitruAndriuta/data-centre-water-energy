"""Q1 on Google's own basis: FRESHWATER withdrawal. Removes the non-potable / reclaimed / seawater
volumes that the reports itemise (Douglas County, Eemshaven, St. Ghislain potable splits).
Hamina is kept: every edition states reported water metrics exclude seawater, so its figures are already freshwater."""
import pandas as pd
from common import OUT, POTABLE_WITHDRAWAL

d = pd.read_csv(OUT / "scarcity_weighted_panel.csv")
d["W_fresh"] = [POTABLE_WITHDRAWAL.get((l, y), w) for l, y, w in zip(d.location, d.year, d.W)]
lines = []
for y in range(2022, 2026):
    s = d[d.year == y]
    lines.append(f"{y}: freshwater withdrawal from High+ stress (bws>=3) {s[s.bws_score>=3].W_fresh.sum()/s.W_fresh.sum()*100:5.1f}%  "
                 f"| from depletion >=2 {s[s.bwd_score>=2].W_fresh.sum()/s.W_fresh.sum()*100:5.1f}%  "
                 f"| St. Ghislain freshwater {s[s.location=='St. Ghislain, Belgium'].W_fresh.sum():.1f} of {s[s.location=='St. Ghislain, Belgium'].W.sum():.1f}")
lines.append("Google (freshwater withdrawal, all operations, own risk framework): 15% (2023, g2024 p.~70), 14% (2024, g2025 appendix), 13% (2025, g2026 appendix). Unitemised non-potable at other sites is still counted as fresh, so these are upper bounds.")
print("\n".join(lines))
with open(OUT / "scarcity_results.txt", "a") as f:
    f.write("\n\n=== Q1 on freshwater basis ===\n" + "\n".join(lines))

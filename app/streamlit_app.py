"""streamlit_app.py — optional UI to browse the generated passport.

Run:
    streamlit run app/streamlit_app.py

Planned panels:
  * KPI row (item count, total cost, total embodied carbon)
  * the material-distribution chart
  * a filterable table of the 64 passport records (by Discipline / Category)
  * the Page-1 building metadata (bonus B3)

This is a convenience viewer over output/passport.json — it does not run the
extraction itself.
"""
from __future__ import annotations

# TODO: implement in the app step (import streamlit lazily so the core
# pipeline has no hard dependency on it).


def main() -> None:
    raise NotImplementedError  # TODO: build the Streamlit UI


if __name__ == "__main__":
    main()

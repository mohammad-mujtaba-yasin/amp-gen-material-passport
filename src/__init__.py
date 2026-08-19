"""AMP-GEN — Material Passport extraction pipeline.

Package layout (data flows top to bottom):

    render      PDF scan pages         -> PNG page images
    extract     page images (vision)   -> raw BoQ items  (-> data/boq_items.json)
    parse       description text       -> material / grade / mix ratio / dimensions / discipline
    normalize   raw quantity + unit    -> canonical unit + routed Volume/Area/Length/Weight/Count
    classify    item                   -> material category, DSR schedule/code, classification match
    carbon      item (bonus B2)        -> density, GWP/kg, embodied carbon A1-A3
    passport    enriched items         -> full passport records (keyed by template header)
    fill_excel  records                -> output/passport_filled.xlsx
    export_json records                -> output/passport.json
    visualize   records                -> output/material_distribution.png
    pipeline    orchestrates the whole run (+ output/building_meta.json, bonus B3)
"""

__version__ = "0.1.0"

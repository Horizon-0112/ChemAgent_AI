"""
Database seed script — populates DB with virtual chemical data.
Run once on first startup or when resetting the database.
"""

import asyncio
from sqlalchemy import select
from database.connection import async_session, init_db
from database.models import Chemical, Catalyst, MsdsData, Dataset, DEMO_DATASET_ID


# ── Chemical Data ────────────────────────────────────────────
CHEMICALS = [
    {"id":"PM-001","name":"PolyEther-K200","category":"Polymer","sub_category":"Engineering Plastic","molecular_weight":28500,"heat_resistance":285,"tensile_strength":72.5,"elongation":15.3,"eco_score":78,"density":1.24,"hazard_level":"low","cost_per_kg":12.5,"compatible_with":["CT-001","CT-003","CT-007"],"color":"#4fc3f7"},
    {"id":"PM-002","name":"NylonFlex-6T","category":"Polymer","sub_category":"Engineering Plastic","molecular_weight":31200,"heat_resistance":310,"tensile_strength":85.0,"elongation":12.1,"eco_score":65,"density":1.38,"hazard_level":"low","cost_per_kg":18.3,"compatible_with":["CT-002","CT-005"],"color":"#7c4dff"},
    {"id":"PM-003","name":"BioPolyLac-300","category":"Polymer","sub_category":"Biodegradable","molecular_weight":18000,"heat_resistance":165,"tensile_strength":52.0,"elongation":8.5,"eco_score":95,"density":1.25,"hazard_level":"low","cost_per_kg":22.0,"compatible_with":["CT-001","CT-006"],"color":"#69f0ae"},
    {"id":"PM-004","name":"PEEK-Ultra","category":"Polymer","sub_category":"High Performance","molecular_weight":42000,"heat_resistance":340,"tensile_strength":100.0,"elongation":30.0,"eco_score":45,"density":1.3,"hazard_level":"low","cost_per_kg":85.0,"compatible_with":["CT-003","CT-008"],"color":"#ff6e40"},
    {"id":"PM-005","name":"EpoxyTech-550","category":"Polymer","sub_category":"Thermoset","molecular_weight":5200,"heat_resistance":220,"tensile_strength":68.0,"elongation":4.2,"eco_score":42,"density":1.18,"hazard_level":"medium","cost_per_kg":15.7,"compatible_with":["CT-002","CT-004","CT-009"],"color":"#ffd740"},
    {"id":"PM-006","name":"SilkFiber-BN","category":"Polymer","sub_category":"Natural Polymer","molecular_weight":75000,"heat_resistance":170,"tensile_strength":45.0,"elongation":22.0,"eco_score":92,"density":1.34,"hazard_level":"low","cost_per_kg":35.0,"compatible_with":["CT-006","CT-010"],"color":"#b388ff"},
    {"id":"PM-007","name":"PolyImide-HT","category":"Polymer","sub_category":"High Performance","molecular_weight":55000,"heat_resistance":400,"tensile_strength":120.0,"elongation":7.5,"eco_score":30,"density":1.42,"hazard_level":"medium","cost_per_kg":120.0,"compatible_with":["CT-003","CT-008"],"color":"#ff5252"},
    {"id":"PM-008","name":"AcryPlast-200","category":"Polymer","sub_category":"General Purpose","molecular_weight":22000,"heat_resistance":95,"tensile_strength":55.0,"elongation":5.0,"eco_score":60,"density":1.19,"hazard_level":"low","cost_per_kg":8.5,"compatible_with":["CT-001","CT-004"],"color":"#40c4ff"},
    {"id":"PM-009","name":"PolyCarbX-700","category":"Polymer","sub_category":"Engineering Plastic","molecular_weight":34000,"heat_resistance":260,"tensile_strength":65.0,"elongation":110.0,"eco_score":55,"density":1.2,"hazard_level":"low","cost_per_kg":14.0,"compatible_with":["CT-002","CT-005","CT-007"],"color":"#e040fb"},
    {"id":"PM-010","name":"PPSulfide-900","category":"Polymer","sub_category":"High Performance","molecular_weight":48000,"heat_resistance":370,"tensile_strength":95.0,"elongation":2.5,"eco_score":35,"density":1.35,"hazard_level":"medium","cost_per_kg":45.0,"compatible_with":["CT-003","CT-008","CT-009"],"color":"#ffab40"},
    {"id":"RS-001","name":"PhenolResin-A1","category":"Resin","sub_category":"Thermoset","molecular_weight":3500,"heat_resistance":200,"tensile_strength":45.0,"elongation":1.5,"eco_score":38,"density":1.28,"hazard_level":"high","cost_per_kg":9.0,"compatible_with":["CT-004","CT-009"],"color":"#8d6e63"},
    {"id":"RS-002","name":"UreaForm-X","category":"Resin","sub_category":"Amino Resin","molecular_weight":2800,"heat_resistance":150,"tensile_strength":38.0,"elongation":1.0,"eco_score":30,"density":1.5,"hazard_level":"high","cost_per_kg":6.5,"compatible_with":["CT-004"],"color":"#a1887f"},
    {"id":"RS-003","name":"VinylEster-Pro","category":"Resin","sub_category":"Unsaturated Resin","molecular_weight":4200,"heat_resistance":190,"tensile_strength":75.0,"elongation":5.5,"eco_score":48,"density":1.12,"hazard_level":"medium","cost_per_kg":11.0,"compatible_with":["CT-002","CT-009"],"color":"#ce93d8"},
    {"id":"RS-004","name":"SiliconeR-HT","category":"Resin","sub_category":"Silicone Resin","molecular_weight":8500,"heat_resistance":350,"tensile_strength":30.0,"elongation":200.0,"eco_score":70,"density":1.05,"hazard_level":"low","cost_per_kg":28.0,"compatible_with":["CT-006","CT-010"],"color":"#90caf9"},
    {"id":"AD-001","name":"NanoSilica-F","category":"Additive","sub_category":"Reinforcing Filler","molecular_weight":60,"heat_resistance":1700,"tensile_strength":0,"elongation":0,"eco_score":72,"density":2.2,"hazard_level":"medium","cost_per_kg":25.0,"compatible_with":["CT-001","CT-003"],"color":"#e0e0e0"},
    {"id":"AD-002","name":"CarbonNT-X","category":"Additive","sub_category":"Nano Reinforcement","molecular_weight":12,"heat_resistance":3000,"tensile_strength":0,"elongation":0,"eco_score":50,"density":1.4,"hazard_level":"high","cost_per_kg":500.0,"compatible_with":["CT-003","CT-008"],"color":"#424242"},
    {"id":"AD-003","name":"GlassFiber-S2","category":"Additive","sub_category":"Fiber Reinforcement","molecular_weight":0,"heat_resistance":840,"tensile_strength":0,"elongation":0,"eco_score":55,"density":2.49,"hazard_level":"low","cost_per_kg":3.5,"compatible_with":["CT-001","CT-002","CT-009"],"color":"#e8eaf6"},
    {"id":"AD-004","name":"FlameGuard-P","category":"Additive","sub_category":"Flame Retardant","molecular_weight":430,"heat_resistance":300,"tensile_strength":0,"elongation":0,"eco_score":25,"density":1.68,"hazard_level":"high","cost_per_kg":18.0,"compatible_with":["CT-004","CT-009"],"color":"#ef5350"},
    {"id":"AD-005","name":"UVStab-220","category":"Additive","sub_category":"Stabilizer","molecular_weight":326,"heat_resistance":250,"tensile_strength":0,"elongation":0,"eco_score":68,"density":1.08,"hazard_level":"low","cost_per_kg":32.0,"compatible_with":["CT-001","CT-005"],"color":"#fff176"},
    {"id":"AD-006","name":"PlastiSoft-E","category":"Additive","sub_category":"Plasticizer","molecular_weight":390,"heat_resistance":80,"tensile_strength":0,"elongation":0,"eco_score":40,"density":0.98,"hazard_level":"medium","cost_per_kg":7.5,"compatible_with":["CT-001","CT-004"],"color":"#80deea"},
    {"id":"PM-011","name":"PTFE-SlickCoat","category":"Polymer","sub_category":"Fluoropolymer","molecular_weight":100000,"heat_resistance":327,"tensile_strength":25.0,"elongation":350.0,"eco_score":20,"density":2.15,"hazard_level":"low","cost_per_kg":65.0,"compatible_with":["CT-010"],"color":"#b0bec5"},
    {"id":"PM-012","name":"PolyUreth-Flex","category":"Polymer","sub_category":"Elastomer","molecular_weight":15000,"heat_resistance":120,"tensile_strength":40.0,"elongation":550.0,"eco_score":50,"density":1.12,"hazard_level":"medium","cost_per_kg":11.0,"compatible_with":["CT-002","CT-004","CT-006"],"color":"#ffcc80"},
    {"id":"PM-013","name":"HDPE-GreenMax","category":"Polymer","sub_category":"General Purpose","molecular_weight":200000,"heat_resistance":130,"tensile_strength":32.0,"elongation":900.0,"eco_score":82,"density":0.95,"hazard_level":"low","cost_per_kg":2.5,"compatible_with":["CT-001","CT-005"],"color":"#66bb6a"},
    {"id":"PM-014","name":"PPCopoly-R","category":"Polymer","sub_category":"General Purpose","molecular_weight":180000,"heat_resistance":160,"tensile_strength":35.0,"elongation":600.0,"eco_score":80,"density":0.91,"hazard_level":"low","cost_per_kg":3.0,"compatible_with":["CT-001","CT-005","CT-007"],"color":"#26c6da"},
    {"id":"PM-015","name":"LCP-ArrowX","category":"Polymer","sub_category":"High Performance","molecular_weight":30000,"heat_resistance":335,"tensile_strength":185.0,"elongation":2.0,"eco_score":32,"density":1.4,"hazard_level":"low","cost_per_kg":75.0,"compatible_with":["CT-003","CT-008"],"color":"#ec407a"},
    {"id":"PM-016","name":"PLA-EcoBlend","category":"Polymer","sub_category":"Biodegradable","molecular_weight":120000,"heat_resistance":155,"tensile_strength":50.0,"elongation":6.0,"eco_score":97,"density":1.24,"hazard_level":"low","cost_per_kg":4.5,"compatible_with":["CT-001","CT-006"],"color":"#81c784"},
    {"id":"PM-017","name":"PBT-ToughGrade","category":"Polymer","sub_category":"Engineering Plastic","molecular_weight":38000,"heat_resistance":225,"tensile_strength":56.0,"elongation":50.0,"eco_score":58,"density":1.31,"hazard_level":"low","cost_per_kg":10.0,"compatible_with":["CT-002","CT-005","CT-007"],"color":"#ab47bc"},
    {"id":"PM-018","name":"PSulfone-Clear","category":"Polymer","sub_category":"Engineering Plastic","molecular_weight":35000,"heat_resistance":275,"tensile_strength":70.0,"elongation":50.0,"eco_score":42,"density":1.24,"hazard_level":"low","cost_per_kg":22.0,"compatible_with":["CT-003","CT-007"],"color":"#5c6bc0"},
    {"id":"PM-019","name":"CelluNano-G","category":"Polymer","sub_category":"Natural Polymer","molecular_weight":500000,"heat_resistance":200,"tensile_strength":140.0,"elongation":10.0,"eco_score":98,"density":1.5,"hazard_level":"low","cost_per_kg":40.0,"compatible_with":["CT-006","CT-010"],"color":"#a5d6a7"},
    {"id":"PM-020","name":"ABS-ProImpact","category":"Polymer","sub_category":"General Purpose","molecular_weight":90000,"heat_resistance":105,"tensile_strength":43.0,"elongation":20.0,"eco_score":55,"density":1.05,"hazard_level":"low","cost_per_kg":5.5,"compatible_with":["CT-001","CT-004","CT-005"],"color":"#78909c"},
]

CATALYSTS = [
    {"id":"CT-001","name":"ZrO-Cat Alpha","type":"Metal Oxide","activation_temp":180,"selectivity":92,"toxicity":"low","lifetime":2400,"cost_per_kg":55.0,"effect_on_strength":1.08,"effect_on_heat_res":1.05,"effect_on_eco":0.98,"description":"General-purpose polymerization catalyst with high selectivity under mild conditions."},
    {"id":"CT-002","name":"TiCl4-NanoDisp","type":"Ziegler-Natta","activation_temp":75,"selectivity":88,"toxicity":"medium","lifetime":1800,"cost_per_kg":120.0,"effect_on_strength":1.15,"effect_on_heat_res":1.02,"effect_on_eco":0.90,"description":"Specialized for olefin polymerization. Enhances crystallinity through stereoregularity."},
    {"id":"CT-003","name":"Pt-Pd Bimetal","type":"Noble Metal","activation_temp":250,"selectivity":97,"toxicity":"low","lifetime":5000,"cost_per_kg":8500.0,"effect_on_strength":1.20,"effect_on_heat_res":1.18,"effect_on_eco":0.85,"description":"High-temperature, high-performance polymer synthesis. Extreme selectivity and durability."},
    {"id":"CT-004","name":"SnOct-R200","type":"Organometallic","activation_temp":120,"selectivity":78,"toxicity":"medium","lifetime":1200,"cost_per_kg":35.0,"effect_on_strength":1.00,"effect_on_heat_res":0.95,"effect_on_eco":0.88,"description":"PU and epoxy curing catalyst. Fast reaction kinetics."},
    {"id":"CT-005","name":"MgCl2-Support","type":"Supported","activation_temp":60,"selectivity":85,"toxicity":"low","lifetime":3200,"cost_per_kg":28.0,"effect_on_strength":1.05,"effect_on_heat_res":1.00,"effect_on_eco":1.02,"description":"Economical catalyst system for polyolefin production."},
    {"id":"CT-006","name":"Lipase-BioEnz","type":"Enzyme","activation_temp":37,"selectivity":99,"toxicity":"low","lifetime":800,"cost_per_kg":450.0,"effect_on_strength":0.95,"effect_on_heat_res":0.85,"effect_on_eco":1.25,"description":"Bio-based polymer synthesis. Highest eco-score enhancement."},
    {"id":"CT-007","name":"FeCp2-Metal","type":"Metallocene","activation_temp":90,"selectivity":94,"toxicity":"low","lifetime":2800,"cost_per_kg":85.0,"effect_on_strength":1.12,"effect_on_heat_res":1.08,"effect_on_eco":0.95,"description":"Homogeneous catalyst for narrow MWD polymers. Precise control."},
    {"id":"CT-008","name":"WC-NanoP","type":"Carbide","activation_temp":350,"selectivity":91,"toxicity":"medium","lifetime":6000,"cost_per_kg":320.0,"effect_on_strength":1.25,"effect_on_heat_res":1.30,"effect_on_eco":0.80,"description":"Ultra-high temperature catalyst for PEEK, polyimide synthesis."},
    {"id":"CT-009","name":"BF3-Initiator","type":"Lewis Acid","activation_temp":25,"selectivity":72,"toxicity":"high","lifetime":600,"cost_per_kg":18.0,"effect_on_strength":1.02,"effect_on_heat_res":0.98,"effect_on_eco":0.70,"description":"Cationic polymerization initiator. Fast but requires fume hood."},
    {"id":"CT-010","name":"SiO2-Aerogel","type":"Porous","activation_temp":150,"selectivity":82,"toxicity":"low","lifetime":4000,"cost_per_kg":200.0,"effect_on_strength":0.98,"effect_on_heat_res":1.10,"effect_on_eco":1.15,"description":"Ultralight porous support catalyst for eco-friendly processes."},
]

MSDS_DATA = [
    {"chemical_id":"PM-001","hazard_classification":"Non-hazardous","ghs_symbols":["GHS07"],"signal_word":"Warning","hazard_statements":["H315: Causes skin irritation","H319: Causes serious eye irritation"],"precautionary_statements":["P261: Avoid breathing dust","P280: Wear protective gloves/eye protection","P305+P351+P338: Rinse eyes with water for several minutes"],"first_aid":{"inhalation":"Move to fresh air. Seek medical advice if symptoms persist.","skinContact":"Remove contaminated clothing. Wash with soap and water.","eyeContact":"Rinse with water for 15+ minutes. Remove contact lenses.","ingestion":"Rinse mouth. Do not induce vomiting. Contact physician."},"storage_conditions":"Sealed container. Away from sunlight. 15-25°C.","disposal_method":"Dispose through approved industrial waste handler.","personal_protection":"Protective gloves, safety goggles, dust mask","emergency_measures":"Maintain ventilation to prevent dust explosion. Contact specialists for large spills."},
    {"chemical_id":"PM-005","hazard_classification":"Hazardous","ghs_symbols":["GHS07","GHS08"],"signal_word":"Warning","hazard_statements":["H315: Causes skin irritation","H317: May cause allergic skin reaction","H319: Causes serious eye irritation","H334: May cause allergy or asthma symptoms if inhaled"],"precautionary_statements":["P261: Avoid breathing vapor/aerosol","P280: Wear protective gloves/eye/face protection","P285: Wear respiratory protection in poorly ventilated areas","P342+P311: If experiencing respiratory symptoms: Call poison center"],"first_aid":{"inhalation":"Move to fresh air immediately. Provide oxygen if breathing is difficult.","skinContact":"Remove contaminated clothing immediately. Wash with soap and water for 15+ minutes.","eyeContact":"Rinse with water for 15+ minutes. Consult ophthalmologist.","ingestion":"Rinse mouth. Do not induce vomiting. Call poison center immediately."},"storage_conditions":"Sealed. Cool, dry place. 10-25°C. Separate from oxidizers.","disposal_method":"Cured: industrial waste. Uncured: hazardous waste disposal.","personal_protection":"Nitrile gloves, safety goggles, organic vapor respirator, protective clothing","emergency_measures":"Remove all ignition sources. Absorb small spills with absorbent material."},
    {"chemical_id":"PM-007","hazard_classification":"Hazardous","ghs_symbols":["GHS07","GHS08"],"signal_word":"Danger","hazard_statements":["H332: Harmful if inhaled","H315: Causes skin irritation","H335: May cause respiratory irritation","H372: Causes damage to organs through prolonged exposure"],"precautionary_statements":["P260: Do not breathe dust","P271: Use only outdoors or in well-ventilated area","P280: Wear protective gloves/eye/face protection","P314: Get medical attention if feeling unwell"],"first_aid":{"inhalation":"Move to fresh air immediately. Medical consultation required.","skinContact":"Wash with plenty of water and soap.","eyeContact":"Rinse with water for 20+ minutes. Consult ophthalmologist immediately.","ingestion":"Do not induce vomiting. Call emergency medical services."},"storage_conditions":"Sealed. Dry location. 15-30°C. Separate from strong acids/bases.","disposal_method":"Dispose through hazardous waste incineration specialist.","personal_protection":"P3 dust mask, double nitrile gloves, safety goggles, full body suit","emergency_measures":"Prevent dust dispersion. Collect with HEPA vacuum. Use water spray for dust suppression."},
    {"chemical_id":"PM-012","hazard_classification":"Hazardous","ghs_symbols":["GHS02","GHS07"],"signal_word":"Warning","hazard_statements":["H315: Causes skin irritation","H319: Causes serious eye irritation","H332: Harmful if inhaled","H227: Combustible liquid (high flash point)"],"precautionary_statements":["P210: Keep away from heat/sparks/flame","P261: Avoid breathing vapor","P280: Wear protective gloves/eye protection"],"first_aid":{"inhalation":"Provide fresh air. Place unconscious person in recovery position.","skinContact":"Wash with water and soap.","eyeContact":"Rinse with water for 15+ minutes.","ingestion":"Do not induce vomiting. Consult physician."},"storage_conditions":"Sealed. No open flame. 5-25°C. Maintain ventilation.","disposal_method":"Cured: general industrial waste. Unreacted: hazardous waste.","personal_protection":"Organic vapor respirator, protective gloves, safety goggles","emergency_measures":"Remove ignition sources. Ventilate. Absorb with sand/vermiculite."},
    {"chemical_id":"RS-001","hazard_classification":"Dangerous","ghs_symbols":["GHS05","GHS07","GHS08"],"signal_word":"Danger","hazard_statements":["H301: Toxic if swallowed","H311: Toxic in contact with skin","H314: Causes severe skin burns and eye damage","H317: May cause allergic skin reaction","H341: Suspected of causing genetic defects","H350: May cause cancer"],"precautionary_statements":["P201: Obtain special instructions before use","P260: Do not breathe vapor/dust","P280: Wear full protective equipment","P301+P310: If swallowed: Call poison center immediately","P303+P361+P353: If on skin: Remove all contaminated clothing and wash"],"first_aid":{"inhalation":"Evacuate immediately. Prepare for artificial respiration. Call emergency services.","skinContact":"Remove all contaminated clothing immediately. Wash with water for 20+ minutes.","eyeContact":"Rinse with water for 30+ minutes. Emergency ophthalmology.","ingestion":"Do NOT induce vomiting. Rinse mouth. Rush to emergency room."},"storage_conditions":"Sealed. Ventilation required. 10-25°C. Absolute separation from oxidizers. Locked storage.","disposal_method":"Certified hazardous chemical waste handler. Never drain to sewage.","personal_protection":"Full-face respirator (organic vapor + formaldehyde), chemical-resistant gloves, full body suit, safety goggles","emergency_measures":"Isolate area immediately. Full ventilation. Call hazmat response team. SCBA required."},
    {"chemical_id":"AD-002","hazard_classification":"Dangerous","ghs_symbols":["GHS07","GHS08"],"signal_word":"Danger","hazard_statements":["H335: May cause respiratory irritation","H373: May cause organ damage through prolonged exposure","H412: Harmful to aquatic life with long lasting effects"],"precautionary_statements":["P260: Do not breathe nanoparticles","P273: Avoid release to environment","P280: Wear P3 dust mask, full body suit","P501: Follow nanomaterial-specific disposal procedures"],"first_aid":{"inhalation":"Evacuate immediately. Provide oxygen if breathing is difficult.","skinContact":"Wash with plenty of water and soap. Check for nanoparticle residue.","eyeContact":"Rinse with water for 20+ minutes. Consult ophthalmologist.","ingestion":"Do not induce vomiting. Call poison center immediately."},"storage_conditions":"Sealed container. Dry. 15-25°C. Separate from oxidizers. Nanomaterial-specific cabinet.","disposal_method":"Certified nanomaterial hazardous waste handler. Never dispose as general waste.","personal_protection":"P3 dust mask, double nitrile gloves, safety goggles, full body suit, shoe covers","emergency_measures":"Isolate area immediately. HEPA vacuum collection. Do NOT use water spray (dispersion risk)."},
    {"chemical_id":"AD-004","hazard_classification":"Dangerous","ghs_symbols":["GHS07","GHS08","GHS09"],"signal_word":"Danger","hazard_statements":["H302: Harmful if swallowed","H315: Causes skin irritation","H410: Very toxic to aquatic life with long lasting effects"],"precautionary_statements":["P273: Avoid release to environment","P280: Wear protective gloves/eye protection","P301+P312: If swallowed and feeling unwell: Call poison center"],"first_aid":{"inhalation":"Move to fresh air.","skinContact":"Wash with water and soap.","eyeContact":"Rinse with water for 15+ minutes.","ingestion":"Rinse mouth. Consult physician."},"storage_conditions":"Sealed. 15-25°C. Isolate from aquatic environments.","disposal_method":"Certified hazardous chemical waste handler. Absolutely no drainage to water systems.","personal_protection":"Protective gloves, safety goggles, dust mask","emergency_measures":"Absorb spills with absorbent material. Absolutely block entry to drains."},
]


async def seed_database():
    """Seed all tables with initial data."""
    await init_db()

    async with async_session() as session:
        # Check if already seeded (Dataset 기준)
        result = await session.execute(
            select(Dataset).where(Dataset.id == DEMO_DATASET_ID)
        )
        if result.scalar():
            print("Database already seeded. Skipping.")
            return

        # Create Demo Dataset record
        demo_dataset = Dataset(
            id=DEMO_DATASET_ID,
            name="Demo Dataset (Built-in)",
            description="Built-in virtual polymer/catalyst dataset for presentation and demo purposes.",
            data_type="demo",
            row_count=len(CHEMICALS) + len(CATALYSTS),
            is_demo=True,
        )
        session.add(demo_dataset)

        # Seed chemicals (with demo dataset_id)
        for data in CHEMICALS:
            session.add(Chemical(**data, dataset_id=DEMO_DATASET_ID))
        print(f"Seeded {len(CHEMICALS)} chemicals.")

        # Seed catalysts (with demo dataset_id)
        for data in CATALYSTS:
            session.add(Catalyst(**data, dataset_id=DEMO_DATASET_ID))
        print(f"Seeded {len(CATALYSTS)} catalysts.")

        # Seed MSDS
        for data in MSDS_DATA:
            session.add(MsdsData(**data))
        print(f"Seeded {len(MSDS_DATA)} MSDS entries.")

        await session.commit()
        print("Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_database())

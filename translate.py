import re
import os

def translate_seed():
    path = "backend/database/seed.py"
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove name_ko
    content = re.sub(r'"name_ko":\s*".*?",\s*', '', content)
    
    # Translate
    translations = {
        '"고분자"': '"Polymer"',
        '"수지"': '"Resin"',
        '"첨가제"': '"Additive"',
        '"엔지니어링 플라스틱"': '"Engineering Plastic"',
        '"생분해성 고분자"': '"Biodegradable Polymer"',
        '"고성능 고분자"': '"High Performance Polymer"',
        '"열경화성 수지"': '"Thermosetting Resin"',
        '"천연 고분자"': '"Natural Polymer"',
        '"범용 플라스틱"': '"General Purpose Plastic"',
        '"불포화 수지"': '"Unsaturated Resin"',
        '"실리콘 수지"': '"Silicone Resin"',
        '"아미노 수지"': '"Amino Resin"',
        '"강화 필러"': '"Reinforcing Filler"',
        '"나노 보강재"': '"Nano Reinforcement"',
        '"섬유 보강재"': '"Fiber Reinforcement"',
        '"난연제"': '"Flame Retardant"',
        '"안정제"': '"Stabilizer"',
        '"가소제"': '"Plasticizer"',
        '"금속산화물 촉매"': '"Metal Oxide Catalyst"',
        '"지글러-나타 촉매"': '"Ziegler-Natta Catalyst"',
        '"귀금속 촉매"': '"Noble Metal Catalyst"',
        '"유기금속 촉매"': '"Organometallic Catalyst"',
        '"지지형 촉매"': '"Supported Catalyst"',
        '"효소 촉매"': '"Enzyme Catalyst"',
        '"메탈로센 촉매"': '"Metallocene Catalyst"',
        '"카바이드 촉매"': '"Carbide Catalyst"',
        '"루이스산 촉매"': '"Lewis Acid Catalyst"',
        '"다공성 촉매"': '"Porous Catalyst"',
        '"위험"': '"Danger"',
        '"경고"': '"Warning"',
        '"비위험물"': '"Non-hazardous"',
        '"유해물질"': '"Hazardous"',
        '"위험물질"': '"Dangerous"',
    }
    for kr, en in translations.items():
        content = content.replace(kr, en)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def translate_chemicals():
    path = "src/data/chemicals.js"
    if not os.path.exists(path): return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove nameKo
    content = re.sub(r'\s*nameKo:\s*".*?",\n', '\n', content)

    translations = {
        '"고분자"': '"Polymer"',
        '"수지"': '"Resin"',
        '"첨가제"': '"Additive"',
        '"엔지니어링 플라스틱"': '"Engineering Plastic"',
        '"생분해성 고분자"': '"Biodegradable Polymer"',
        '"고성능 고분자"': '"High Performance Polymer"',
        '"열경화성 수지"': '"Thermosetting Resin"',
        '"천연 고분자"': '"Natural Polymer"',
        '"범용 플라스틱"': '"General Purpose Plastic"',
        '"불포화 수지"': '"Unsaturated Resin"',
        '"실리콘 수지"': '"Silicone Resin"',
        '"아미노 수지"': '"Amino Resin"',
        '"강화 필러"': '"Reinforcing Filler"',
        '"나노 보강재"': '"Nano Reinforcement"',
        '"섬유 보강재"': '"Fiber Reinforcement"',
        '"난연제"': '"Flame Retardant"',
        '"안정제"': '"Stabilizer"',
        '"가소제"': '"Plasticizer"',
        '"산화방지제"': '"Antioxidant"',
        '"착색제"': '"Colorant"',
        '"불소 고분자"': '"Fluoropolymer"',
        '"엘라스토머"': '"Elastomer"',
        '// ── 고분자 (Polymers) ──────────────────────────────────': '// ── Polymers ──────────────────────────────────',
        '// ── 수지 (Resins) ─────────────────────────────────────': '// ── Resins ─────────────────────────────────────',
        '// ── 첨가제 (Additives) ────────────────────────────────': '// ── Additives ────────────────────────────────',
        '// ── 추가 고분자 ───────────────────────────────────────': '// ── Additional Polymers ───────────────────────────────────────',
    }
    for kr, en in translations.items():
        content = content.replace(kr, en)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    translate_seed()
    translate_chemicals()
    print("Done")

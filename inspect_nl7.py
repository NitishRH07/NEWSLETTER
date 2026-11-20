import sqlite3
import json

conn = sqlite3.connect('d:/Hobby/AI_NEWSLETTER/newsletter.db')
c = conn.cursor()
c.execute('SELECT pdf_path, json_path, template_name FROM newsletters WHERE id = 7')
row = c.fetchone()
print(f"PDF: {row[0]} | JSON: {row[1]} | Template: {row[2]}")

with open(row[1], 'r', encoding='utf-8') as f:
    data = json.load(f)

for idx, tool in enumerate(data['tools'], 1):
    name = tool.get('name')
    cat = tool.get('category')
    print(f"\n==================== TOOL {idx}: {name} ====================")
    print(f"Category: {cat}")
    print("HOW IT WORKS STEPS:")
    for s in tool.get('how_it_works_steps', []):
        print(f"  [{s.get('step')}] {s.get('title')}: {s.get('desc')}")
    print("WHERE IT HELPS:")
    for h in tool.get('where_it_helps', []):
        print(f"  {h.get('icon')} {h.get('title')}: {h.get('desc')}")
    snap = tool.get('feature_snapshot', {})
    print("FEATURE SNAPSHOT:")
    print(f"  INPUT: {snap.get('input_title')} -> {snap.get('input_desc')}")
    print(f"  AI STEP: {snap.get('ai_step_title')} -> {snap.get('ai_step_desc')}")
    print(f"  OUTPUT: {snap.get('output_title')} -> {snap.get('output_desc')}")
    print(f"  ADVANTAGE: {snap.get('key_advantage')}")
    print(f"HAL USE CASE: {tool.get('hal_use_case')}")
    print(f"HAL EXAMPLE WORKFLOW: {tool.get('hal_example_workflow')}")

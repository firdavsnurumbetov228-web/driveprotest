# -*- coding: utf-8 -*-
import sys

with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if 'if is_active:' in line:
        start_idx = i
    if 'await message.answer(text, parse_mode=' in line and start_idx != -1:
        end_idx = i
        break

if start_idx == -1 or end_idx == -1:
    print("Could not find block.")
    sys.exit(1)

new_code = """    if is_active:
        # ── Allaqachon faollashtirilgan ──
        text = (
            "✅ *Siz allaqachon aktivatsiyaga egasiz\\!*\\n\\n"
            "Testlardan to'liq foydalana olasiz\\. 🚗"
            if lang == "uz"
            else
            "✅ *У вас уже есть активация\\!*\\n\\n"
            "Вы можете пользоваться тестами в полном объёме\\. 🚗"
        )
    else:
        # ── Hali faollashtirilmagan ──
        text = (
            "💳 *Aktivatsiya*\\n\\n"
            "Aktivatsiya uchun admin bilan bog'laning:\\n"
            "@DRIVE\\_PRO\\_admin\\n\\n"
            "📞 Tel: \\+998940907300"
            if lang == "uz"
            else
            "💳 *Активация*\\n\\n"
            "Для активации свяжитесь с администратором:\\n"
            "@DRIVE\\_PRO\\_admin\\n\\n"
            "📞 Тел: \\+998940907300"
        )
    await message.answer(text, parse_mode="MarkdownV2")
"""

del lines[start_idx:end_idx+1]
lines.insert(start_idx, new_code)

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
    
print("SUCCESS")

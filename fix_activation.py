# -*- coding: utf-8 -*-
# Activation handler ni to'g'ridan-to'g'ri qatorlar orqali patch qilish

with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 452-476 qatorlarni (0-indexed: 451-475) yangi kod bilan almashtirish
new_lines = []
i = 0
while i < len(lines):
    # 452-chi qator (0-indexed 451) - "    if is_active:"
    if i == 451:
        new_lines.append("    if is_active:\n")
        new_lines.append("        # \u2500\u2500 Allaqachon faollashtirilgan \u2500\u2500\n")
        new_lines.append("        if lang == \"uz\":\n")
        new_lines.append("            text = (\n")
        new_lines.append("                \"\u2705 *Siz allaqachon aktivatsiyaga egasiz\\!*\\n\\n\"\n")
        new_lines.append("                \"Testlardan to'liq foydalana olasiz\\. \ud83d\ude97\"\n")
        new_lines.append("            )\n")
        new_lines.append("        else:\n")
        new_lines.append("            text = (\n")
        new_lines.append("                \"\u2705 *\u0423 \u0432\u0430\u0441 \u0443\u0436\u0435 \u0435\u0441\u0442\u044c \u0430\u043a\u0442\u0438\u0432\u0430\u0446\u0438\u044f\\!*\\n\\n\"\n")
        new_lines.append("                \"\u0412\u044b \u043c\u043e\u0436\u0435\u0442\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c\u0441\u044f \u0442\u0435\u0441\u0442\u0430\u043c\u0438 \u0432 \u043f\u043e\u043b\u043d\u043e\u043c \u043e\u0431\u044a\u0451\u043c\u0435\\. \ud83d\ude97\"\n")
        new_lines.append("            )\n")
        new_lines.append("    else:\n")
        new_lines.append("        # \u2500\u2500 Hali faollashtirilmagan \u2500\u2500\n")
        new_lines.append("        if lang == \"uz\":\n")
        new_lines.append("            text = (\n")
        new_lines.append("                \"\ud83d\udcb3 *Aktivatsiya*\\n\\n\"\n")
        new_lines.append("                \"Aktivatsiya uchun admin bilan bog'laning:\\n\"\n")
        new_lines.append("                \"@DRIVE\\_PRO\\_admin\\n\\n\"\n")
        new_lines.append("                \"\ud83d\udcde Tel: \\+998940907300\"\n")
        new_lines.append("            )\n")
        new_lines.append("        else:\n")
        new_lines.append("            text = (\n")
        new_lines.append("                \"\ud83d\udcb3 *\u0410\u043a\u0442\u0438\u0432\u0430\u0446\u0438\u044f*\\n\\n\"\n")
        new_lines.append("                \"\u0414\u043b\u044f \u0430\u043a\u0442\u0438\u0432\u0430\u0446\u0438\u0438 \u0441\u0432\u044f\u0436\u0438\u0442\u0435\u0441\u044c \u0441 \u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440\u043e\u043c:\\n\"\n")
        new_lines.append("                \"@DRIVE\\_PRO\\_admin\\n\\n\"\n")
        new_lines.append("                \"\ud83d\udcde \u0422\u0435\u043b: \\+998940907300\"\n")
        new_lines.append("            )\n")
        new_lines.append("    await message.answer(text, parse_mode=\"MarkdownV2\")\n")
        # Skip old lines 451-475 (0-indexed)
        i = 476  # jump to line 477 (0-indexed 476)
        continue
    new_lines.append(lines[i])
    i += 1

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Done! Total lines: {len(new_lines)}")

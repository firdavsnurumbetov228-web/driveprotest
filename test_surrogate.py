import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')

from aiohttp import FormData
from urllib.parse import urlencode

text = (
    "💳 *Активация*\n\n"
    "Для активации свяжитесь с администратором:\n"
    "@DRIVE\\_PRO\\_admin\n\n"
    "📞 Тел: \\+998940907300"
)

print("Text repr:", repr(text))
print("Text starts with:", repr(text[0]), "ord:", hex(ord(text[0])))
print("Has surrogates:", any(0xD800 <= ord(c) <= 0xDFFF for c in text))

# Test urlencode directly  
try:
    result = urlencode([('text', text)], doseq=True, encoding='utf-8')
    print("urlencode OK:", result[:100])
except UnicodeEncodeError as e:
    print("urlencode FAILED:", e)

# Test FormData
try:
    fd = FormData(quote_fields=False)
    fd.add_field('text', text)
    fd.add_field('chat_id', '123')
    fd.add_field('parse_mode', 'MarkdownV2')
    payload = fd()
    print("FormData OK:", type(payload))
except UnicodeEncodeError as e:
    print("FormData FAILED:", e)

print("\nTest with simulated surrogate:")
# Create a string with actual surrogates (simulating what might happen)
bad_text = "\ud83d\udcb3 test"
print("Bad text repr:", repr(bad_text))
try:
    result = urlencode([('text', bad_text)], doseq=True, encoding='utf-8')
    print("urlencode OK")
except UnicodeEncodeError as e:
    print("urlencode FAILED:", e)

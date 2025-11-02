# tickets/utils.py
import hmac
import hashlib
from urllib.parse import quote_plus
import requests
from django.conf import settings
from django.core.files.base import ContentFile

QR_API_BASE = "https://api.qrserver.com/v1/create-qr-code/"

def make_signature(ticket_uuid: str) -> str:
    key = settings.TICKET_HMAC_KEY.encode()
    msg = ticket_uuid.encode()
    sig = hmac.new(key, msg, hashlib.sha256).hexdigest()
    return sig

def verify_signature(ticket_uuid: str, sig: str) -> bool:
    expected = make_signature(ticket_uuid)
    return hmac.compare_digest(expected, sig)

def build_payload(ticket_uuid: str, signature: str) -> str:
    return f"{ticket_uuid}|{signature}"

def generate_qr_and_save(ticket, payload_str: str, size: str = "300x300") -> str:
    encoded = quote_plus(payload_str)
    url = f"{QR_API_BASE}?data={encoded}&size={size}"
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"QR API returned {resp.status_code}")
    filename = f"ticket_{ticket.id}.png"
    content = ContentFile(resp.content)
    ticket.qr_image.save(filename, content, save=False)
    return ticket.qr_image.url

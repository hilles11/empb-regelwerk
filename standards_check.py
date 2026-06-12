import hashlib
import html
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone


SOURCES = {
    "vdaBand2": "https://webshop.vda.de/QMC/de/search?q=Sicherung+der+Qualit%C3%A4t+von+Lieferungen",
    "iatfSIs": "https://www.iatfglobaloversight.org/iatf-169492016/iatf-169492016-sis/",
    "iatfCsrs": "https://www.iatfglobaloversight.org/oem-requirements/customer-specific-requirements/",
    "aiagPpap": "https://www.aiag.org/store/publications/details?ProductCode=PPAP-4",
}


def fetch(url):
    last_error = None
    for attempt in range(3):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/125 Safari/537.36 EMPB-Monitor/1.0",
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=40) as response:
                body = response.read().decode("utf-8", "replace")
                if len(body) < 5000:
                    raise ValueError("Quelle lieferte keine vollständig auswertbare Seite.")
                return body
        except Exception as error:
            last_error = error
            if attempt < 2:
                time.sleep(2 + attempt * 2)
    raise last_error


def text_content(source):
    source = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", source)
    source = re.sub(r"(?s)<[^>]+>", " ", source)
    return re.sub(r"\s+", " ", html.unescape(source)).strip()


def normalized_hash(values):
    normalized = "\n".join(sorted(set(re.sub(r"\s+", " ", value).strip() for value in values if value.strip())))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def inspect_vda(source):
    text = text_content(source)
    matches = re.findall(r"(?i).{0,100}(?:Band\s*0?2|Sicherung der Qualität von Lieferungen).{0,180}", text)
    years = sorted(set(re.findall(r"\b20\d{2}\b", " ".join(matches))))
    editions = sorted(set(re.findall(r"(?i)\b\d+\.\s*(?:überarbeitete\s+)?Auflage\b", " ".join(matches))))
    if not matches or not years:
        raise ValueError("VDA Band 2 konnte auf der offiziellen Seite nicht eindeutig erkannt werden.")
    return {
        "signal": normalized_hash(matches),
        "display": f"VDA Band 2 · {' / '.join(editions) or 'Auflage öffentlich nicht eindeutig'} · {' / '.join(years) or 'Jahr nicht erkannt'}",
        "details": matches[:5],
    }


def inspect_iatf_sis(source):
    text = text_content(source)
    found = re.findall(
        r"(?i)IATF\s*16949:2016\s+Sanctioned Interpretations.*?#\s*(\d+)\s*[-–]\s*(\d+).*?issued\s+([A-Za-z]+\s+\d{4})",
        text,
    )
    if not found:
        found = re.findall(r"(?i)#\s*(\d+)\s*[-–]\s*(\d+).{0,80}?([A-Za-z]+\s+\d{4})", text)
    latest = max(found, key=lambda item: int(item[1])) if found else None
    if not latest:
        raise ValueError("Der öffentliche IATF-SI-Stand konnte nicht eindeutig erkannt werden.")
    return {
        "signal": f"{latest[0]}-{latest[1]}|{latest[2]}" if latest else normalized_hash([text[:5000]]),
        "display": f"IATF SIs Nr. {latest[0]}–{latest[1]} · {latest[2]}" if latest else "IATF SIs · Stand nicht eindeutig erkannt",
        "details": sorted(set(f"#{start}-{end} · {date}" for start, end, date in found)),
    }


def inspect_iatf_csrs(source):
    text = text_content(source)
    entries = re.findall(
        r"(?i)(?:BMW|BYD|Ford|Geely|General Motors|IVECO|Jaguar Land Rover|Mercedes-Benz|Renault|Stellantis|Volkswagen|Volvo).{0,180}?(?:20\d{2}|under development)",
        text,
    )
    if len(set(entries)) < 5:
        raise ValueError("Die öffentliche IATF-CSR-Liste konnte nicht vollständig erkannt werden.")
    return {
        "signal": normalized_hash(entries),
        "display": f"IATF Customer Specific Requirements · {len(set(entries))} öffentliche Einträge erkannt",
        "details": sorted(set(entries))[:30],
    }


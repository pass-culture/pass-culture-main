RESPONSE_SAFE_URL = {
    "data": {
        "id": "e68d31b2889529733c242bf310120b94753776491077f1f923bd2494fb0c6976",
        "type": "url",
        "links": {
            "self": "https://www.virustotal.com/api/v3/urls/e68d31b2889529733c242bf310120b94753776491077f1f923bd2494fb0c6976"
        },
        "attributes": {
            "last_analysis_date": 1702580877,
            "last_analysis_results": {
                "AV1": {"method": "blacklist", "engine_name": "AV1", "category": "undetected", "result": "unrated"},
                "AV2": {"method": "blacklist", "engine_name": "AV2", "category": "harmless", "result": "clean"},
                "AV3": {"method": "blacklist", "engine_name": "AV3", "category": "harmless", "result": "clean"},
                "AV4": {"method": "blacklist", "engine_name": "AV4", "category": "undetected", "result": "unrated"},
                "AV5": {"method": "blacklist", "engine_name": "AV5", "category": "harmless", "result": "clean"},
            },
            "url": "https://passculture.pro/",
            "last_http_response_content_sha256": "41ebecc0bdc468f791a323e46299fe1ccbbc9c5dd038412fdd737c98d0fe44de",
            "total_votes": {"harmless": 0, "malicious": 0},
            "times_submitted": 12,
            "last_http_response_headers": {
                "Content-Length": "1908",
                "X-Served-By": "cache-chi-klot8100111-CHI",
                "X-Cache": "HIT",
                "Content-Encoding": "br",
                "Accept-Ranges": "bytes",
                "X-Timer": "S1702600757.426247,VS0,VE1",
                "Vary": "x-fh-requested-host, accept-encoding",
                "Last-Modified": "Tue, 12 Dec 2023 14:59:09 GMT",
                "Connection": "keep-alive",
                "Etag": '"c0926a97ec48c95ccad8fe001d3da37191d7d4371a1eec79e2f4c1e1ce6ccaa7-br"',
                "X-Cache-Hits": "1",
                "Strict-Transport-Security": "max-age=31556926",
                "Cache-Control": "max-age=3600",
                "Date": "Fri, 15 Dec 2023 00:39:17 GMT",
                "alt-svc": 'h3=":443";ma=86400,h3-29=":443";ma=86400,h3-27=":443";ma=86400',
                "Content-Type": "text/html; charset=utf-8",
            },
            "last_modification_date": 1702601068,
            "last_http_response_content_length": 1908,
            "categories": {"AV6": "misc", "AV7": "entertainment", "AV8": "news and media"},
            "first_submission_date": 1634896025,
            "html_meta": {},
            "last_submission_date": 1702580877,
            "last_final_url": "https://passculture.pro/",
            "title": "pass Culture Pro",
            "reputation": 0,
            "tld": "pro",
            "threat_names": [],
            "tags": [],
            "last_analysis_stats": {"malicious": 0, "suspicious": 0, "undetected": 2, "harmless": 3, "timeout": 0},
            "last_http_response_code": 200,
        },
    }
}

RESPONSE_MALICIOUS_URL = {
    "data": {
        "id": "018b1c22d6a45012986a1b06c059019faa57e8c76e7dab5c11ecf4ccd334343d",
        "type": "url",
        "links": {
            "self": "https://www.virustotal.com/api/v3/urls/018b1c22d6a45012986a1b06c059019faa57e8c76e7dab5c11ecf4ccd334343d"
        },
        "attributes": {
            "last_analysis_date": 1712740333,
            "last_http_response_code": 200,
            "redirection_chain": ["https://malicious.com/"],
            "last_http_response_headers": {
                "content-encoding": "gzip",
                "content-type": "text/html; charset=UTF-8",
                "date": "Wed, 10 Apr 2024 09:12:21 GMT",
                "link": '<https://www.malicious.com/wp-json/>; rel="https://api.w.org/"\n<https://www.malicious.com/wp-json/wp/v2/pages/17>; rel="alternate"; type="application/json"\n<https://www.malicious.com/>; rel=shortlink',
                "server": "Apache",
                "vary": "Accept-Encoding",
                "x-powered-by": "PHP/7.4",
            },
            "tld": "com",
            "trackers": {},
            "last_modification_date": 1712740658,
            "last_http_response_content_length": 130362,
            "threat_names": [],
            "total_votes": {"harmless": 0, "malicious": 0},
            "url": "https://malicious.com/",
            "first_submission_date": 1692966836,
            "last_analysis_stats": {"malicious": 2, "suspicious": 1, "undetected": 1, "harmless": 3, "timeout": 0},
            "last_http_response_content_sha256": "27318b2eaad2cb908a9a47521c6eb08655e4f1986f9bb78a158180e46736a0de",
            "title": "L\u2019association - malicious",
            "times_submitted": 4,
            "last_submission_date": 1712740333,
            "last_analysis_results": {
                "AV1": {"method": "blacklist", "engine_name": "AV1", "category": "harmless", "result": "clean"},
                "AV2": {"method": "blacklist", "engine_name": "AV2", "category": "malicious", "result": "malicious"},
                "AV3": {"method": "blacklist", "engine_name": "AV3", "category": "harmless", "result": "clean"},
                "AV4": {"method": "blacklist", "engine_name": "AV4", "category": "undetected", "result": "unrated"},
                "AV5": {"method": "blacklist", "engine_name": "AV5", "category": "harmless", "result": "clean"},
                "AV6": {"method": "blacklist", "engine_name": "AV6", "category": "malicious", "result": "malicious"},
                "AV7": {"method": "blacklist", "engine_name": "AV7", "category": "suspicious", "result": "suspicious"},
            },
            "categories": {"AV7": "Business/Economy, Suspicious (alphaMountain.ai)"},
            "html_meta": {},
            "tags": ["external-resources", "trackers", "iframes", "third-party-cookies", "dom-modification"],
            "outgoing_links": [
                "https://www.example.com/",
            ],
            "last_final_url": "https://www.malicious.com/",
            "reputation": 0,
        },
    }
}

RESPONSE_URL_PENDING = {
    "data": {
        "attributes": {
            "categories": {},
            "first_submission_date": 1764692665,
            "last_analysis_results": {},
            "last_modification_date": 1764692668,
            "last_submission_date": 1764692665,
            "reputation": 0,
            "times_submitted": 1,
            "tld": "com",
            "total_votes": {"harmless": "0", "malicious": "0"},
            "url": "https://www.example.com",
        },
        "id": "cd541e6cb931f4a120cf6da1095a1fe945d9c0b7090525a0ed5c4ef7630af1f6",
        "links": {
            "self": "https://www.virustotal.com/api/v3/urls/cd541e6cb931f4a120cf6da1095a1fe945d9c0b7090525a0ed5c4ef7630af1f6"
        },
        "type": "url",
    }
}


RESPONSE_URL_NOT_FOUND = {
    "error": {"code": "NotFoundError", "message": 'URL "aHR0cHM6Ly93d3cubm90LWZvdW5kLmNvbQ" not found'}
}

RESPONSE_URL_ANALYSE = {
    "data": {
        "type": "analysis",
        "id": "u-e68d31b2889529733c242bf310120b94753776491077f1f923bd2494fb0c6976-1712762695",
        "links": {
            "self": "https://www.virustotal.com/api/v3/analyses/u-e68d31b2889529733c242bf310120b94753776491077f1f923bd2494fb0c6976-1712762695"
        },
    }
}

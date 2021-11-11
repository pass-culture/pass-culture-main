from flask import jsonify
from flask.wrappers import Response

from pcapi.routes.apis import public_api


# WARNING: those routes are required for universal links - ie links to the
# native application - to work.
# They are not attached to the native_v1 blueprint because they must be at
# the server's root.


@public_api.route("/.well-known/apple-app-site-association", methods=["GET"])
def apple_app_site_association() -> Response:
    response = jsonify(
        {
            "applinks": {
                "appIDs": [
                    "WBC4X3LRTS.app.passculture.test",
                    "WBC4X3LRTS.app.passculture.staging",
                    "WBC4X3LRTS.app.passculture",
                ],
                "components": [{"/": "*", "comment": "Matchs every routes and lets app decides which accept"}],
            },
            "webcredentials": {
                "appIDs": [
                    "WBC4X3LRTS.app.passculture.test",
                    "WBC4X3LRTS.app.passculture.staging",
                    "WBC4X3LRTS.app.passculture",
                ]
            },
        }
    )
    response.content_type = "application/pkcs7-mime"
    return response


@public_api.route("/.well-knwon/assetlinks.json", methods=["GET"])
def asset_links() -> Response:
    response = jsonify(
        [
            {
                "relation": ["delegate_permission/common.handle_all_urls"],
                "target": {
                    "namespace": "PassCulture T",
                    "package_name": "com.passculture",
                    "sha256_cert_fingerprints": [
                        "F2:59:8C:3F:07:B3:8E:6D:D0:20:A8:1B:A1:02:7B:82:41:53:88:D8:84:0E:CB:22:87:CC:CD:12:F0:8E:32:7F"
                    ],
                },
            }
        ]
    )
    response.content_type = "application/pkcs7-mime"
    return response

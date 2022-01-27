from pcapi.connectors.dms import api as api_dms


client = api_dms.DMSGraphQLClient()

data = client.get_single_application_details(7555183)

for annotation in data["dossier"]["annotations"]:
    if annotation["label"] == "Données validées par l' API":
        response = client.update_checkbox_annotation(
            dossier_id=data["dossier"]["id"],
            instructeur_id="SW5zdHJ1Y3RldXItNTY5OTQ=",
            annotation_id=annotation["id"],
            value=True,
        )
    if annotation["label"] == "Champs en erreur":
        response = client.update_text_annotation(
            dossier_id=data["dossier"]["id"],
            instructeur_id="SW5zdHJ1Y3RldXItNTY5OTQ=",
            annotation_id=annotation["id"],
            value="""Erreur dans les champs :
            - xxx
            - yyy
            """,
        )

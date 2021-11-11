import typing


def make_dms_wrong_values_data(
    postal_code_value: typing.Optional[str], id_piece_number_value: typing.Optional[str]
) -> dict:
    data = {
        "Mj-TemplateID": 3124925,
        "Mj-TemplateLanguage": True,
        "Vars": {},
    }
    if postal_code_value:
        data["Vars"]["field_name1"] = "Code Postal"
        data["Vars"]["field_input1"] = postal_code_value
    if id_piece_number_value:
        data["Vars"]["field_name2"] = "N° de pièce d'identité"
        data["Vars"]["field_input2"] = id_piece_number_value
    return data

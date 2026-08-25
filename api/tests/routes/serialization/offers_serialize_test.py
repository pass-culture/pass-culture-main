import pytest

from pcapi.routes.serialization.offers_serialize import PatchOfferBodyModel


class PatchOfferBodyModelExtraDataTest:
    @pytest.mark.parametrize("key", ["gtl_id", "csr_id", "nb_pages", "musicType", "showSubType", "ean"])
    def should_validate_keys_under_their_declared_name(self, key):
        body = PatchOfferBodyModel(extraData={key: "x"})

        assert body.extraData == {key: "x"}

    def should_dump_extra_data_under_its_declared_names(self):
        body = PatchOfferBodyModel(extraData={"gtl_id": "010101010", "showType": "400"})

        updates = body.model_dump(by_alias=True, exclude_unset=True)

        assert updates["extraData"] == {"gtl_id": "010101010", "showType": "400"}

    @pytest.mark.parametrize("key", ["malicious_data", "show_type"])
    def should_reject_unknown_keys(self, key):
        with pytest.raises(ValueError) as error:
            PatchOfferBodyModel(extraData={key: "400"})

        assert error.value.errors()[0]["type"] == "extra_forbidden"

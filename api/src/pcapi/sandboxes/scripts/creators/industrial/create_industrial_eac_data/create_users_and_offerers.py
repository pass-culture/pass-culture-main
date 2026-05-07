from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


@log_func_duration
def create_eac_users_offerers() -> dict[str, offerers_models.Offerer]:
    offerer_by_name = {}

    name = "eac_1_lieu"
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="eac_1_lieu@example.com",
        offerer__name=name,
        offerer__siren="552081317",
    )
    offerer_by_name[name] = user_offerer.offerer

    name = "eac_2_lieu [BON EAC]"
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="eac_2_lieu@example.com",
        offerer__name=name,
        offerer__siren="444608442",
        offerer__allowedOnAdage=True,
    )
    offerer_by_name[name] = user_offerer.offerer

    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="retention_structures@example.com",
        offerer=user_offerer.offerer,
    )
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="squad-eac@passculture.app",
        offerer=user_offerer.offerer,
    )

    # user with 2 offerer 1 eac and 1 non eac
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="half_eac@example.com",
        offerer=user_offerer.offerer,
    )
    offerers_factories.UserOffererFactory.create(
        user=user_offerer.user,
        offerer__name="no_eac",
        offerer__siren="542107651",
    )

    name = "eac_pending_bank_informations"
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="eac_pending_bank_informations@example.com",
        offerer__name=name,
        offerer__siren="552046955",
    )
    finance_factories.BankAccountFactory.create(
        offerer=user_offerer.offerer,
        status=BankAccountApplicationStatus.ON_GOING,
    )
    offerer_by_name[name] = user_offerer.offerer

    name = "eac_no_cb"
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="eac_no_cb@example.com",
        offerer__name=name,
        offerer__siren="444786511",
    )
    offerer_by_name[name] = user_offerer.offerer

    name = "eac_rejected"
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="eac_rejected@example.com",
        offerer__name=name,
        offerer__siren="897492294",
        offerer__allowedOnAdage=False,
    )
    offerer_by_name[name] = user_offerer.offerer

    # DMS state
    name = "eac_accepte"
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="eac_accepte@example.com",
        offerer__name=name,
        offerer__siren="538160524",
    )
    offerer_by_name[name] = user_offerer.offerer

    name = "eac_sans_suite"
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="eac_sans_suite@example.com",
        offerer__name=name,
        offerer__siren="538160656",
        offerer__allowedOnAdage=False,
    )
    offerer_by_name[name] = user_offerer.offerer

    name = "eac_en_construction"
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="eac_en_construction@example.com",
        offerer__name=name,
        offerer__siren="843082389",
        offerer__allowedOnAdage=False,
    )
    offerer_by_name[name] = user_offerer.offerer

    name = "eac_refuse"
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="eac_refuse@example.com",
        offerer__name=name,
        offerer__siren="524237351",
        offerer__allowedOnAdage=False,
    )
    offerer_by_name[name] = user_offerer.offerer

    name = "eac_en_instruction"
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="eac_en_instruction@example.com",
        offerer__name=name,
        offerer__siren="538160615",
        offerer__allowedOnAdage=False,
    )
    offerer_by_name[name] = user_offerer.offerer

    name = "eac_complete_30+d"
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="eac_complete_30d@example.com",
        offerer__name=name,
        offerer__siren="456500537",
    )
    offerer_by_name[name] = user_offerer.offerer

    name = "eac_complete_30-d"
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="eac_complete_30-d@example.com",
        offerer__name=name,
        offerer__siren="848009452",
    )
    offerer_by_name[name] = user_offerer.offerer

    name = "eac_with_two_adage_venues"
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="eac_with_two_adage_venues@example.com",
        offerer__name=name,
        offerer__siren="848171500",
    )
    offerer_by_name[name] = user_offerer.offerer

    name = "eac_with_no_offers"
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="eac_with_no_offers@example.com",
        offerer__name=name,
        offerer__siren="956513147",
    )
    offerer_by_name[name] = user_offerer.offerer

    name = "eac_with_application_with_no_venue"
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="eac_with_application_with_no_venue@example.com",
        offerer__name=name,
        offerer__siren="956513154",
    )
    offerer_by_name[name] = user_offerer.offerer

    name = "eac_with_displayed_status_cases"
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="eac_with_displayed_status_cases@example.com",
        offerer__name=name,
        offerer__siren="662042449",
        offerer__allowedOnAdage=True,
    )
    offerer_by_name[name] = user_offerer.offerer

    name = "eac_with_deposits_by_period"
    user_offerer = offerers_factories.UserOffererFactory.create(
        user__email="eac_with_deposits_by_period@example.com",
        offerer__name=name,
        offerer__siren="552120230",
        offerer__allowedOnAdage=True,
    )
    offerer_by_name[name] = user_offerer.offerer

    return offerer_by_name

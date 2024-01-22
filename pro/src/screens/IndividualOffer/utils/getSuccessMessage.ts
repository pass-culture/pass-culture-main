import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared'

export const getSuccessMessage = (mode: OFFER_WIZARD_MODE) => {
  switch (mode) {
    case OFFER_WIZARD_MODE.CREATION:
      return 'Brouillon sauvegardé dans la liste des offres'

    case OFFER_WIZARD_MODE.EDITION:
    default:
      return PATCH_SUCCESS_MESSAGE
  }
}

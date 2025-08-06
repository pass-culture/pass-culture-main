import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { PATCH_SUCCESS_MESSAGE } from '@/commons/core/shared/constants'

export const getSuccessMessage = (mode: OFFER_WIZARD_MODE) => {
  switch (mode) {
    case OFFER_WIZARD_MODE.CREATION:
      return 'Brouillon sauvegardé dans la liste des offres'

    case OFFER_WIZARD_MODE.EDITION:
    case OFFER_WIZARD_MODE.READ_ONLY:
    default:
      return PATCH_SUCCESS_MESSAGE
  }
}

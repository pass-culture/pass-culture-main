import { OFFER_WIZARD_MODE } from 'core/Offers/constants'

export const getSuccessMessage = (mode: OFFER_WIZARD_MODE) => {
  switch (mode) {
    case OFFER_WIZARD_MODE.CREATION:
    case OFFER_WIZARD_MODE.DRAFT:
      return 'Brouillon sauvegardé dans la liste des offres'

    case OFFER_WIZARD_MODE.EDITION:
    default:
      return 'Vos modifications ont bien été enregistrées'
  }
}

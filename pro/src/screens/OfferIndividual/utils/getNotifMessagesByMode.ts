import { OFFER_WIZARD_MODE } from 'core/Offers'

export const getSuccessMessage = (mode: OFFER_WIZARD_MODE) =>
  ({
    [OFFER_WIZARD_MODE.CREATION]:
      'Brouillon sauvegardé dans la liste des offres',
    [OFFER_WIZARD_MODE.DRAFT]: 'Brouillon sauvegardé dans la liste des offres',
    [OFFER_WIZARD_MODE.EDITION]: 'Vos modifications ont bien été enregistrées',
  })[mode]

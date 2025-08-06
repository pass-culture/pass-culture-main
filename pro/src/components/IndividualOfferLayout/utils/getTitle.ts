import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'

export const getTitle = (mode: OFFER_WIZARD_MODE) =>
  ({
    [OFFER_WIZARD_MODE.CREATION]: 'Créer une offre',
    [OFFER_WIZARD_MODE.READ_ONLY]: 'Consulter l’offre',
    [OFFER_WIZARD_MODE.EDITION]: 'Modifier l’offre',
  })[mode]

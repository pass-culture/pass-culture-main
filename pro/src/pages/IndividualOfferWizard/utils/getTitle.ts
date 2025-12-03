import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'

export const getTitle = (mode: OFFER_WIZARD_MODE, offerName: string) =>
  ({
    [OFFER_WIZARD_MODE.CREATION]: 'Créer une offre',
    [OFFER_WIZARD_MODE.READ_ONLY]: offerName,
    [OFFER_WIZARD_MODE.EDITION]: 'Modifier l’offre',
  })[mode]

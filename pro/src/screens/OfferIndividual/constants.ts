import { TStepPatternList } from 'new_components/Breadcrumb'

export enum OFFER_FORM_STEP_IDS {
  INFORMATIONS = 'informations',
  STOCKS = 'stocks',
  SUMMARY = 'recapitulatif',
  CONFIRMATION = 'confirmation',
}

export const CREATION_STEP_PATTERNS: TStepPatternList = {
  [OFFER_FORM_STEP_IDS.INFORMATIONS]: {
    id: OFFER_FORM_STEP_IDS.INFORMATIONS,
    label: 'Informations',
    url: '/offre/v3/creation/individuelle/informations',
    path: '/offre/:offerId/v3/creation/individuelle/informations',
  },
  [OFFER_FORM_STEP_IDS.STOCKS]: {
    id: OFFER_FORM_STEP_IDS.STOCKS,
    label: 'Stock & Prix',
    path: '/offre/:offerId/v3/creation/individuelle/stocks',
  },
  [OFFER_FORM_STEP_IDS.SUMMARY]: {
    id: OFFER_FORM_STEP_IDS.SUMMARY,
    label: 'Récapitulatif',
    path: '/offre/:offerId/v3/creation/individuelle/recapitulatif',
  },
  [OFFER_FORM_STEP_IDS.CONFIRMATION]: {
    id: OFFER_FORM_STEP_IDS.CONFIRMATION,
    label: 'Confirmation',
    path: '/offre/:offerId/v3/creation/individuelle/confirmation',
  },
}

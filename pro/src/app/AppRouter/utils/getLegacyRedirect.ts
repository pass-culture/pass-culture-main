import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'

export interface ILegacyRedirect {
  redirectFrom: string
  redirectTo: string
}

interface IGetLegacyRedirectArgs {
  isV2: boolean
}

const getLegacyRedirect = ({
  isV2 = false,
}: IGetLegacyRedirectArgs): ILegacyRedirect[] => [
  {
    redirectFrom: '/offres/:offerId([A-Z0-9]+)/edition',
    redirectTo: getOfferIndividualPath({
      step: OFFER_WIZARD_STEP_IDS.SUMMARY,
      mode: OFFER_WIZARD_MODE.EDITION,
      isV2,
    }),
  },
  {
    redirectFrom: '/offre/:offerId([A-Z0-9]+)/scolaire/edition',
    redirectTo: '/offre/:offerId([A-Z0-9]+)/collectif/edition',
  },
]

export default getLegacyRedirect

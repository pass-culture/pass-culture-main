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
}: IGetLegacyRedirectArgs): ILegacyRedirect[] => {
  let legacyRedirect: ILegacyRedirect[] = [
    {
      // redirect offer v1 route
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

  if (!isV2) {
    const redirectMap = Object.values(OFFER_WIZARD_STEP_IDS)
      .map(step => {
        return Object.values(OFFER_WIZARD_MODE).map(mode => ({ step, mode }))
      })
      .flat()
      .filter(
        ({ step, mode }) =>
          mode !== OFFER_WIZARD_MODE.EDITION ||
          step !== OFFER_WIZARD_STEP_IDS.CONFIRMATION
      )

    legacyRedirect = [
      ...legacyRedirect,
      {
        redirectFrom: getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.EDITION,
          isV2: true,
          isCreation: true,
        }),
        redirectTo: getOfferIndividualPath({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.EDITION,
          isV2: false,
          isCreation: true,
        }),
      },
      ...redirectMap.map(({ step, mode }) => {
        return {
          redirectFrom: getOfferIndividualPath({
            step,
            mode,
            isV2: true,
          }),
          redirectTo: getOfferIndividualPath({
            step,
            mode,
            isV2: false,
          }),
        }
      }),
    ]
  }

  return legacyRedirect
}

export default getLegacyRedirect

import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'

import { getAfterSubmitPath } from './getAfterSubmitPath'

describe('getAfterSubmitPath', () => {
  it('should redirect to the edition step in read-only mode in EDITION mode', () => {
    expect(
      getAfterSubmitPath({
        offerId: 10,
        mode: OFFER_WIZARD_MODE.EDITION,
        isOnboarding: false,
        isOfferExposureEnabled: false,
        currentStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
        followingStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS,
      })
    ).toBe('/offre/individuelle/10/tarifs')
  })

  it('should stay on the page (return undefined) in EDITION mode when offer exposure is enabled', () => {
    expect(
      getAfterSubmitPath({
        offerId: 10,
        mode: OFFER_WIZARD_MODE.EDITION,
        isOnboarding: false,
        isOfferExposureEnabled: true,
        currentStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
        followingStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS,
      })
    ).toBeUndefined()
  })

  it('should redirect to the creation step in CREATION mode', () => {
    expect(
      getAfterSubmitPath({
        offerId: 10,
        mode: OFFER_WIZARD_MODE.CREATION,
        isOnboarding: false,
        isOfferExposureEnabled: false,
        currentStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
        followingStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS,
      })
    ).toBe('/offre/individuelle/10/creation/informations_pratiques')
  })

  it('should prefix the path with /onboarding when onboarding', () => {
    expect(
      getAfterSubmitPath({
        offerId: 10,
        mode: OFFER_WIZARD_MODE.CREATION,
        isOnboarding: true,
        isOfferExposureEnabled: false,
        currentStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
        followingStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA,
      })
    ).toBe('/onboarding/offre/individuelle/10/creation/media')
  })
})

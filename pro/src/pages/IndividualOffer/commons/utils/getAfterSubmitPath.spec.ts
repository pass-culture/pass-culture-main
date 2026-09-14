import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'

import { getAfterSubmitPath } from './getAfterSubmitPath'

describe('getAfterSubmitPath', () => {
  it('should stay on the page in EDITION mode', () => {
    expect(
      getAfterSubmitPath({
        offerId: 10,
        mode: OFFER_WIZARD_MODE.EDITION,
        isOnboarding: false,
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
        followingStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA,
      })
    ).toBe('/onboarding/offre/individuelle/10/creation/media')
  })
})

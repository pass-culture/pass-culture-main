import { DEFAULT_EAC_FORM_VALUES } from 'core/OfferEducational/constants'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'

import { computeInitialValuesFromOffer } from '../computeInitialValuesFromOffer'

describe('computeInitialValuesFromOffer', () => {
  it('should return default values when no offer is provided', () => {
    expect(
      computeInitialValuesFromOffer(
        { educationalCategories: [], educationalSubCategories: [] },
        []
      )
    ).toEqual(DEFAULT_EAC_FORM_VALUES)
  })

  it('should use email for notification emails if notification email not set', () => {
    expect(
      computeInitialValuesFromOffer(
        { educationalCategories: [], educationalSubCategories: [] },
        [],
        collectiveOfferFactory({
          contactEmail: 'someemail@example.com',
          bookingEmails: undefined,
        })
      ).notificationEmails
    ).toEqual(['someemail@example.com'])
  })
})

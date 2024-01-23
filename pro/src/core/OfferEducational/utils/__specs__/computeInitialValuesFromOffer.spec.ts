import { DEFAULT_EAC_FORM_VALUES } from 'core/OfferEducational/constants'
import {
  collectiveOfferFactory,
  collectiveOfferTemplateFactory,
} from 'utils/collectiveApiFactories'
import { formatShortDateForInput } from 'utils/date'

import { computeInitialValuesFromOffer } from '../computeInitialValuesFromOffer'

describe('computeInitialValuesFromOffer', () => {
  it('should return default values when no offer is provided', () => {
    expect(
      computeInitialValuesFromOffer(
        { educationalCategories: [], educationalSubCategories: [] },
        [],
        false
      )
    ).toEqual(DEFAULT_EAC_FORM_VALUES)
  })

  it('should use email for notification emails if notification email not set', () => {
    expect(
      computeInitialValuesFromOffer(
        { educationalCategories: [], educationalSubCategories: [] },
        [],
        false,
        collectiveOfferFactory({
          contactEmail: 'someemail@example.com',
          bookingEmails: undefined,
        })
      ).notificationEmails
    ).toEqual(['someemail@example.com'])
  })

  it('should pre-set todays dates for a template offer creation initial values', () => {
    expect(
      computeInitialValuesFromOffer(
        { educationalCategories: [], educationalSubCategories: [] },
        [],
        true,
        undefined
      ).beginningDate
    ).toEqual(formatShortDateForInput(new Date()))
  })

  it('should fill the time values to the start date time', () => {
    expect(
      computeInitialValuesFromOffer(
        { educationalCategories: [], educationalSubCategories: [] },
        [],
        true,
        collectiveOfferTemplateFactory({
          dates: {
            end: '2024-01-29T23:00:28.040559Z',
            start: '2024-01-23T23:00:28.040547Z',
          },
        })
      ).hour
    ).toEqual('23:00')
  })
})

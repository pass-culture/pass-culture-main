import { OfferContactFormEnum } from 'apiClient/v1'
import { DEFAULT_EAC_FORM_VALUES } from 'commons/core/OfferEducational/constants'
import { formatShortDateForInput } from 'commons/utils/date'
import { getCollectiveOfferTemplateFactory } from 'commons/utils/factories/collectiveApiFactories'
import { venueListItemFactory } from 'commons/utils/factories/individualApiFactories'

import { computeInitialValuesFromOffer } from '../computeInitialValuesFromOffer'

const venues = [venueListItemFactory()]

describe('computeInitialValuesFromOffer', () => {
  it('should return default values when no offer is provided', () => {
    expect(computeInitialValuesFromOffer(null, false, venues)).toEqual(
      DEFAULT_EAC_FORM_VALUES
    )
  })

  it('should pre-set todays dates for a template offer creation initial values', () => {
    expect(
      computeInitialValuesFromOffer(null, true, venues, undefined).beginningDate
    ).toEqual(formatShortDateForInput(new Date()))
  })

  it('should fill the time values to the start date time', () => {
    expect(
      computeInitialValuesFromOffer(
        null,
        true,
        venues,
        getCollectiveOfferTemplateFactory({
          dates: {
            end: '2024-01-29T23:00:28.040559Z',
            start: '2024-01-23T23:00:28.040547Z',
          },
        })
      ).hour
    ).toEqual('23:00')
  })

  it('should create a default template offer form with custom contact options', () => {
    expect(
      computeInitialValuesFromOffer(
        null,
        true,
        venues,
        undefined,
        undefined,
        false
      )
    ).toEqual(
      expect.objectContaining({
        contactOptions: { email: false, phone: false, form: false },
        contactFormType: 'form',
      })
    )
  })

  it('should create a template from an offer with offer email', () => {
    expect(
      computeInitialValuesFromOffer(
        null,
        true,
        venues,
        getCollectiveOfferTemplateFactory({
          contactEmail: 'email@test.co',
          contactPhone: null,
        }),
        undefined,
        false
      )
    ).toEqual(
      expect.objectContaining({
        contactOptions: { email: true, phone: false, form: false },
        email: 'email@test.co',
      })
    )
  })

  it('should create a template from an offer with offer phone', () => {
    expect(
      computeInitialValuesFromOffer(
        null,
        true,
        venues,
        getCollectiveOfferTemplateFactory({
          contactEmail: undefined,
          contactPhone: '00000000',
        }),
        undefined,
        false
      )
    ).toEqual(
      expect.objectContaining({
        contactOptions: { email: false, phone: true, form: false },
        phone: '00000000',
      })
    )
  })

  it('should create a template from an offer with offer form url', () => {
    expect(
      computeInitialValuesFromOffer(
        null,
        true,
        venues,
        getCollectiveOfferTemplateFactory({
          contactEmail: undefined,
          contactPhone: undefined,
          contactForm: undefined,
          contactUrl: 'http://testurl.com',
        }),
        undefined,
        false
      )
    ).toEqual(
      expect.objectContaining({
        contactOptions: { email: false, phone: false, form: true },
        contactUrl: 'http://testurl.com',
      })
    )
  })

  it('should create a template from an offer with offer default form', () => {
    expect(
      computeInitialValuesFromOffer(
        null,
        true,
        venues,
        getCollectiveOfferTemplateFactory({
          contactEmail: undefined,
          contactPhone: undefined,
          contactForm: OfferContactFormEnum.FORM,
          contactUrl: undefined,
        }),
        undefined,
        false
      )
    ).toEqual(
      expect.objectContaining({
        contactOptions: { email: false, phone: false, form: true },
      })
    )
  })
})

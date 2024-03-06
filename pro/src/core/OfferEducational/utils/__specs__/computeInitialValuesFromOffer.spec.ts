import { OfferContactFormEnum } from 'apiClient/v1'
import { DEFAULT_EAC_FORM_VALUES } from 'core/OfferEducational/constants'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from 'utils/collectiveApiFactories'
import { formatShortDateForInput } from 'utils/date'

import { computeInitialValuesFromOffer } from '../computeInitialValuesFromOffer'

describe('computeInitialValuesFromOffer', () => {
  it('should return default values when no offer is provided', () => {
    expect(computeInitialValuesFromOffer([], false)).toEqual(
      DEFAULT_EAC_FORM_VALUES
    )
  })

  it('should use email for notification emails if notification email not set', () => {
    expect(
      computeInitialValuesFromOffer(
        [],
        false,
        getCollectiveOfferFactory({
          contactEmail: 'someemail@example.com',
          bookingEmails: undefined,
        })
      ).notificationEmails
    ).toEqual(['someemail@example.com'])
  })

  it('should pre-set todays dates for a template offer creation initial values', () => {
    expect(
      computeInitialValuesFromOffer([], true, undefined).beginningDate
    ).toEqual(formatShortDateForInput(new Date()))
  })

  it('should fill the time values to the start date time', () => {
    expect(
      computeInitialValuesFromOffer(
        [],
        true,
        getCollectiveOfferTemplateFactory({
          dates: {
            end: '2024-01-29T23:00:28.040559Z',
            start: '2024-01-23T23:00:28.040547Z',
          },
        })
      ).hour
    ).toEqual('23:00')
  })

  it('should create a default template offer form with custom contact options if the ff is enabled', () => {
    expect(
      computeInitialValuesFromOffer(
        [],
        true,
        undefined,
        undefined,
        undefined,
        false,
        true
      )
    ).toEqual(
      expect.objectContaining({
        contactOptions: { email: false, phone: false, form: false },
        contactFormType: 'form',
      })
    )
  })

  it('should create a template from an offer with offer email if ff is enabled', () => {
    expect(
      computeInitialValuesFromOffer(
        [],
        true,
        getCollectiveOfferTemplateFactory({
          contactEmail: 'email@test.co',
          contactPhone: null,
        }),
        undefined,
        undefined,
        false,
        true
      )
    ).toEqual(
      expect.objectContaining({
        contactOptions: { email: true, phone: false, form: false },
        email: 'email@test.co',
      })
    )
  })

  it('should create a template from an offer with offer phone if ff is enabled', () => {
    expect(
      computeInitialValuesFromOffer(
        [],
        true,
        getCollectiveOfferTemplateFactory({
          contactEmail: undefined,
          contactPhone: '00000000',
        }),
        undefined,
        undefined,
        false,
        true
      )
    ).toEqual(
      expect.objectContaining({
        contactOptions: { email: false, phone: true, form: false },
        phone: '00000000',
      })
    )
  })

  it('should create a template from an offer with offer form url if ff is enabled', () => {
    expect(
      computeInitialValuesFromOffer(
        [],
        true,
        getCollectiveOfferTemplateFactory({
          contactEmail: undefined,
          contactPhone: undefined,
          contactForm: undefined,
          contactUrl: 'http://testurl.com',
        }),
        undefined,
        undefined,
        false,
        true
      )
    ).toEqual(
      expect.objectContaining({
        contactOptions: { email: false, phone: false, form: true },
        contactUrl: 'http://testurl.com',
      })
    )
  })

  it('should create a template from an offer with offer default form if ff is enabled', () => {
    expect(
      computeInitialValuesFromOffer(
        [],
        true,
        getCollectiveOfferTemplateFactory({
          contactEmail: undefined,
          contactPhone: undefined,
          contactForm: OfferContactFormEnum.FORM,
          contactUrl: undefined,
        }),
        undefined,
        undefined,
        false,
        true
      )
    ).toEqual(
      expect.objectContaining({
        contactOptions: { email: false, phone: false, form: true },
      })
    )
  })

  it('should not build the contact options if the ff is disabled', () => {
    const formValues = computeInitialValuesFromOffer(
      [],
      true,
      getCollectiveOfferTemplateFactory({
        contactEmail: 'email@test.co',
        contactUrl: 'http://url.com',
        contactForm: OfferContactFormEnum.FORM,
      }),
      undefined,
      undefined,
      false,
      false
    )
    expect(formValues.contactOptions).toEqual(undefined)

    expect(formValues.email).toEqual('email@test.co')

    expect(formValues.contactUrl).toEqual(undefined)
  })
})

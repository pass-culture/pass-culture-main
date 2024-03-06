import { DEFAULT_EAC_FORM_VALUES } from 'core/OfferEducational/constants'

import {
  createCollectiveOfferPayload,
  createCollectiveOfferTemplatePayload,
} from '../createOfferPayload'

describe('createOfferPayload', () => {
  it('should remove dates from a template offer to create a non-template offer', () => {
    expect(
      Object.keys(
        createCollectiveOfferPayload({
          ...DEFAULT_EAC_FORM_VALUES,
          beginningDate: '2021-09-01',
          endingDate: '2021-09-10',
        })
      )
    ).toEqual(expect.not.arrayContaining(['dates']))
  })

  it('should not remove dates from an offer to create a template offer', () => {
    expect(
      createCollectiveOfferTemplatePayload(
        {
          ...DEFAULT_EAC_FORM_VALUES,
          beginningDate: '2021-09-01',
          endingDate: '2021-09-10',
          datesType: 'specific_dates',
        },
        false
      ).dates
    ).toBeTruthy()
  })

  it('should remove dates from an offer that has no valid dates to create a template offer', () => {
    expect(
      createCollectiveOfferTemplatePayload(
        {
          ...DEFAULT_EAC_FORM_VALUES,
          beginningDate: undefined,
          endingDate: undefined,
        },
        false
      ).dates
    ).toBeFalsy()
  })

  it('should create a template offer payload with email infos when the ff is enabled and the email option is checked in the form', () => {
    const offerPayload = createCollectiveOfferTemplatePayload(
      {
        ...DEFAULT_EAC_FORM_VALUES,
        contactOptions: {
          email: true,
          phone: false,
          form: false,
        },
        email: 'email@email.com',
        phone: '12345',
        contactFormType: 'url',
        contactUrl: 'http://url.com',
      },
      true
    )
    expect(Object.keys(offerPayload)).toEqual(
      expect.not.arrayContaining(['phone', 'contactUrl'])
    )

    expect(offerPayload).toEqual(
      expect.objectContaining({ contactEmail: 'email@email.com' })
    )
  })

  it('should create a template offer payload with phone infos when the ff is enabled and the phone option is checked in the form', () => {
    const offerPayload = createCollectiveOfferTemplatePayload(
      {
        ...DEFAULT_EAC_FORM_VALUES,
        contactOptions: {
          email: false,
          phone: true,
          form: false,
        },
        email: 'email@email.com',
        phone: '12345',
        contactFormType: 'url',
        contactUrl: 'http://url.com',
      },
      true
    )
    expect(Object.keys(offerPayload)).toEqual(
      expect.not.arrayContaining(['email', 'contactUrl'])
    )

    expect(offerPayload).toEqual(
      expect.objectContaining({ contactPhone: '12345' })
    )
  })

  it('should create a template offer payload with url infos when the ff is enabled and the form option is checked in the form', () => {
    const offerPayload = createCollectiveOfferTemplatePayload(
      {
        ...DEFAULT_EAC_FORM_VALUES,
        contactOptions: {
          email: false,
          phone: false,
          form: true,
        },
        email: 'email@email.com',
        phone: '12345',
        contactFormType: 'url',
        contactUrl: 'http://url.com',
      },
      true
    )
    expect(Object.keys(offerPayload)).toEqual(
      expect.not.arrayContaining(['email', 'phone'])
    )

    expect(offerPayload).toEqual(
      expect.objectContaining({ contactUrl: 'http://url.com' })
    )
  })

  it('should create a template offer payload with the email if the ff is disabled', () => {
    const offerPayload = createCollectiveOfferTemplatePayload(
      {
        ...DEFAULT_EAC_FORM_VALUES,
        contactOptions: {
          email: true,
          phone: true,
          form: true,
        },
        email: 'email@email.com',
        phone: '12345',
        contactFormType: 'url',
        contactUrl: 'http://url.com',
      },
      false
    )

    expect(offerPayload).toEqual(
      expect.objectContaining({
        contactEmail: 'email@email.com',
        contactPhone: '12345',
        contactForm: undefined,
        contactUrl: undefined,
      })
    )
  })
})

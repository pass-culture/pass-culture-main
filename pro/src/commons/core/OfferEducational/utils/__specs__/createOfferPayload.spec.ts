import { OfferAddressType } from 'apiClient/v1'
import { DEFAULT_EAC_FORM_VALUES } from 'commons/core/OfferEducational/constants'

import {
  createCollectiveOfferPayload,
  createCollectiveOfferTemplatePayload,
} from '../createOfferPayload'

describe('createOfferPayload', () => {
  it('should remove dates from a template offer to create a non-template offer', () => {
    expect(
      Object.keys(
        createCollectiveOfferPayload(
          {
            ...DEFAULT_EAC_FORM_VALUES,
            beginningDate: '2021-09-01',
            endingDate: '2021-09-10',
          },
          false
        )
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

  it('should create a template offer payload with email infos when the email option is checked in the form', () => {
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
      false
    )
    expect(Object.keys(offerPayload)).toEqual(
      expect.not.arrayContaining(['phone', 'contactUrl'])
    )

    expect(offerPayload).toEqual(
      expect.objectContaining({ contactEmail: 'email@email.com' })
    )
  })

  it('should create a template offer payload with phone infos when the phone option is checked in the form', () => {
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
      false
    )
    expect(Object.keys(offerPayload)).toEqual(
      expect.not.arrayContaining(['email', 'contactUrl'])
    )

    expect(offerPayload).toEqual(
      expect.objectContaining({ contactPhone: '12345' })
    )
  })

  it('should create a template offer payload with url infos when the form option is checked in the form', () => {
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
      false
    )
    expect(Object.keys(offerPayload)).toEqual(
      expect.not.arrayContaining(['email', 'phone'])
    )

    expect(offerPayload).toEqual(
      expect.objectContaining({ contactUrl: 'http://url.com' })
    )
  })

  it('should create a template offer payload with intervention area infos when the offer address type is SCHOOL', () => {
    const offerPayload = createCollectiveOfferTemplatePayload(
      {
        ...DEFAULT_EAC_FORM_VALUES,
        eventAddress: {
          addressType: OfferAddressType.SCHOOL,
          otherAddress: '',
          venueId: null,
        },
        interventionArea: ['44'],
      },
      false
    )

    expect(offerPayload).toEqual(
      expect.objectContaining({ interventionArea: ['44'] })
    )
  })

  it('should create a template offer payload with intervention area infos when the offer address type is OTHER', () => {
    const offerPayload = createCollectiveOfferTemplatePayload(
      {
        ...DEFAULT_EAC_FORM_VALUES,
        eventAddress: {
          addressType: OfferAddressType.OTHER,
          otherAddress: '4 rue du chat qui pêche',
          venueId: null,
        },
        interventionArea: ['44'],
      },
      false
    )

    expect(offerPayload).toEqual(
      expect.objectContaining({ interventionArea: ['44'] })
    )
  })

  it('should create a template offer payload with empty intervention area infos when the offer address type is OFFERER_VENUE', () => {
    const offerPayload = createCollectiveOfferTemplatePayload(
      {
        ...DEFAULT_EAC_FORM_VALUES,
        eventAddress: {
          addressType: OfferAddressType.OFFERER_VENUE,
          otherAddress: '',
          venueId: 4,
        },
        interventionArea: ['44'],
      },
      false
    )

    expect(offerPayload).toEqual(
      expect.objectContaining({ interventionArea: [] })
    )
  })
})

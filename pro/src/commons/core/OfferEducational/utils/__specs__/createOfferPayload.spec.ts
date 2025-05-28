import { CollectiveLocationType, OfferAddressType } from 'apiClient/v1'
import { getDefaultEducationalValues } from 'commons/core/OfferEducational/constants'

import {
  createCollectiveOfferPayload,
  createCollectiveOfferTemplatePayload,
} from '../createOfferPayload'

const offer = {
  ...getDefaultEducationalValues(),
  location: {
    locationType: CollectiveLocationType.ADDRESS,
    address: {
      isVenueAddress: true,
      id_oa: '123',
      isManualEdition: false,
      label: '',
    },
  },
  city: 'Paris',
  latitude: '3',
  longitude: '2',
  postalCode: '75018',
  street: 'rue de la paix',
  eventAddress: {
    addressType: OfferAddressType.OFFERER_VENUE,
    otherAddress: '',
    venueId: 4,
  },
  interventionArea: ['44'],
}

describe('createOfferPayload', () => {
  it('should remove dates from a template offer to create a non-template offer', () => {
    expect(
      Object.keys(
        createCollectiveOfferPayload(
          {
            ...getDefaultEducationalValues(),
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
          ...getDefaultEducationalValues(),
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
          ...getDefaultEducationalValues(),
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
        ...getDefaultEducationalValues(),
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
        ...getDefaultEducationalValues(),
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
        ...getDefaultEducationalValues(),
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
        ...getDefaultEducationalValues(),
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
        ...getDefaultEducationalValues(),
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
        ...getDefaultEducationalValues(),
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

  it('should create a template offer payload with location infos when OA FF is active', () => {
    const offerPayload = createCollectiveOfferTemplatePayload(
      {
        ...offer,
        location: {
          ...offer.location,
          address: { ...offer.location.address, label: 'théâtre' },
        },
      },
      true
    )

    expect(offerPayload).toEqual(
      expect.objectContaining({
        location: {
          locationType: CollectiveLocationType.ADDRESS,
          address: {
            city: 'Paris',
            latitude: '3',
            longitude: '2',
            postalCode: '75018',
            street: 'rue de la paix',
            isVenueAddress: true,
            isManualEdition: false,
            label: 'théâtre',
            banId: '',
            coords: '',
          },
        },
      })
    )
  })

  it('should create a template offer payload with location infos when OA FF is active and locationType is SCHOOL', () => {
    const offerPayload = createCollectiveOfferTemplatePayload(
      {
        ...offer,
        location: {
          locationType: CollectiveLocationType.SCHOOL,
          address: { isManualEdition: false, isVenueAddress: false, label: '' },
        },
      },
      true
    )

    expect(offerPayload).toEqual(
      expect.objectContaining({
        location: {
          locationType: CollectiveLocationType.SCHOOL,
        },
        interventionArea: ['44'],
      })
    )
  })

  it('should create a template offer payload with location infos when OA FF is active and locationType is TO_BE_DEFINED', () => {
    const offerPayload = createCollectiveOfferTemplatePayload(
      {
        ...offer,
        location: {
          locationType: CollectiveLocationType.TO_BE_DEFINED,
          locationComment: 'to be defined',
        },
      },
      true
    )

    expect(offerPayload).toEqual(
      expect.objectContaining({
        location: {
          locationType: CollectiveLocationType.TO_BE_DEFINED,

          locationComment: 'to be defined',
        },
        interventionArea: ['44'],
      })
    )
  })

  it('should create a template offer payload with offerVenue infos when OA FF is not active', () => {
    const offerPayload = createCollectiveOfferTemplatePayload(offer, false)

    expect(offerPayload).toEqual(
      expect.objectContaining({
        offerVenue: {
          addressType: 'offererVenue',
          otherAddress: '',
          venueId: 4,
        },
      })
    )
  })
})

import { CollectiveLocationType } from '@/apiClient/v1'
import { getDefaultEducationalValues } from '@/commons/core/OfferEducational/constants'

import {
  createCollectiveOfferPayload,
  createCollectiveOfferTemplatePayload,
} from '../createOfferPayload'

const offer = {
  ...getDefaultEducationalValues(),
  location: {
    locationType: CollectiveLocationType.ADDRESS,
    location: {
      isVenueLocation: true,
      id: '123',
      isManualEdition: false,
      label: '',
    },
  },
  city: 'Paris',
  latitude: '3',
  longitude: '2',
  postalCode: '75018',
  street: 'rue de la paix',
  interventionArea: ['44'],
}

describe('createOfferPayload', () => {
  it('should remove dates from a template offer to create a non-template offer', () => {
    expect(
      Object.keys(
        createCollectiveOfferPayload({
          ...getDefaultEducationalValues(),
          beginningDate: '2021-09-01',
          endingDate: '2021-09-10',
        })
      )
    ).toEqual(expect.not.arrayContaining(['dates']))
  })

  it('should not remove dates from an offer to create a template offer', () => {
    expect(
      createCollectiveOfferTemplatePayload({
        ...getDefaultEducationalValues(),
        beginningDate: '2021-09-01',
        endingDate: '2021-09-10',
        datesType: 'specific_dates',
      }).dates
    ).toBeTruthy()
  })

  it('should remove dates from an offer that has no valid dates to create a template offer', () => {
    expect(
      createCollectiveOfferTemplatePayload({
        ...getDefaultEducationalValues(),
        beginningDate: undefined,
        endingDate: undefined,
      }).dates
    ).toBeFalsy()
  })

  it('should create a template offer payload with email infos when the email option is checked in the form', () => {
    const offerPayload = createCollectiveOfferTemplatePayload({
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
    })
    expect(Object.keys(offerPayload)).toEqual(
      expect.not.arrayContaining(['phone', 'contactUrl'])
    )

    expect(offerPayload).toEqual(
      expect.objectContaining({ contactEmail: 'email@email.com' })
    )
  })

  it('should create a template offer payload with phone infos when the phone option is checked in the form', () => {
    const offerPayload = createCollectiveOfferTemplatePayload({
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
    })
    expect(Object.keys(offerPayload)).toEqual(
      expect.not.arrayContaining(['email', 'contactUrl'])
    )

    expect(offerPayload).toEqual(
      expect.objectContaining({ contactPhone: '12345' })
    )
  })

  it('should create a template offer payload with url infos when the form option is checked in the form', () => {
    const offerPayload = createCollectiveOfferTemplatePayload({
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
    })
    expect(Object.keys(offerPayload)).toEqual(
      expect.not.arrayContaining(['email', 'phone'])
    )

    expect(offerPayload).toEqual(
      expect.objectContaining({ contactUrl: 'http://url.com' })
    )
  })

  it('should create a template offer payload with location infos', () => {
    const offerPayload = createCollectiveOfferTemplatePayload({
      ...offer,
      location: {
        ...offer.location,
        location: { ...offer.location.location, label: 'théâtre' },
      },
    })

    expect(offerPayload).toEqual(
      expect.objectContaining({
        location: {
          locationType: CollectiveLocationType.ADDRESS,
          location: {
            isVenueLocation: true,
          },
        },
      })
    )
  })

  it('should create a template offer payload with location infos when locationType is SCHOOL', () => {
    const offerPayload = createCollectiveOfferTemplatePayload({
      ...offer,
      location: {
        locationType: CollectiveLocationType.SCHOOL,
        location: { isManualEdition: false, isVenueLocation: false, label: '' },
      },
    })

    expect(offerPayload).toEqual(
      expect.objectContaining({
        location: {
          locationType: CollectiveLocationType.SCHOOL,
        },
        interventionArea: ['44'],
      })
    )
  })

  it('should create a template offer payload with location infos when locationType is TO_BE_DEFINED', () => {
    const offerPayload = createCollectiveOfferTemplatePayload({
      ...offer,
      location: {
        locationType: CollectiveLocationType.TO_BE_DEFINED,
        locationComment: 'to be defined',
      },
    })

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

  it.each([
    null,
    undefined,
    '',
  ])('should create a template offer payload with location infos and locationType is TO_BE_DEFINED and comment is empty', (comment) => {
    const offerPayload = createCollectiveOfferTemplatePayload({
      ...offer,
      location: {
        locationType: CollectiveLocationType.TO_BE_DEFINED,
        locationComment: comment,
      },
    })

    expect(offerPayload).toEqual(
      expect.objectContaining({
        location: {
          locationType: CollectiveLocationType.TO_BE_DEFINED,

          locationComment: null,
        },
        interventionArea: ['44'],
      })
    )
  })
})

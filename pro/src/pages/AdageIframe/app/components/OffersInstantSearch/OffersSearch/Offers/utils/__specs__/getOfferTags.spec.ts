import {
  CollectiveLocationType,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
  OfferAddressType,
  StudentLevels,
} from 'apiClient/adage'
import {
  defaultAdageUser,
  defaultCollectiveOffer,
  defaultCollectiveTemplateOffer,
} from 'commons/utils/factories/adageFactories'

import { getOfferTags } from '../getOfferTags'

const templateOffer = defaultCollectiveTemplateOffer
const bookableOffer = defaultCollectiveOffer
const adageUser = defaultAdageUser

describe('getOfferTags', () => {
  it('should return the list of tags when the offer happens at school', () => {
    const offer: CollectiveOfferTemplateResponseModel = {
      ...templateOffer,
      dates: { start: '2023-10-23T22:00:00Z', end: '2023-10-24T21:59:00Z' },
      offerVenue: {
        ...templateOffer.offerVenue,
        addressType: OfferAddressType.SCHOOL,
      },
      venue: {
        ...templateOffer.venue,
        coordinates: {
          latitude: 1,
          longitude: 1,
        },
      },
      students: [StudentLevels.COLL_GE_3E],
    }
    const tags = getOfferTags(offer, { ...adageUser, lat: 0, lon: 0 }).map(
      (tag) => tag.text
    )
    const tagsReduced = getOfferTags(
      offer,
      { ...adageUser, lat: 0, lon: 0 },
      false
    ).map((tag) => tag.text)

    expect(tags).toEqual(
      expect.arrayContaining([
        'Dans l’établissement scolaire',
        'Du 23 octobre au 24 octobre 2023 à 22h',
        'Collège - 3e',
        'Partenaire situé à 157 km',
      ])
    )

    expect(tagsReduced).toEqual(['Dans l’établissement scolaire'])
  })

  it('should return the list of tags when the offer happens at school when ff oa is enabled', () => {
    const offer: CollectiveOfferTemplateResponseModel = {
      ...templateOffer,
      dates: { start: '2023-10-23T22:00:00Z', end: '2023-10-24T21:59:00Z' },
      location: {
        locationType: CollectiveLocationType.SCHOOL,
      },
      venue: {
        ...templateOffer.venue,
        coordinates: {
          latitude: 1,
          longitude: 1,
        },
      },
      students: [StudentLevels.COLL_GE_3E],
    }
    const tags = getOfferTags(
      offer,
      { ...adageUser, lat: 0, lon: 0 },
      true,
      true
    ).map((tag) => tag.text)
    const tagsReduced = getOfferTags(
      offer,
      { ...adageUser, lat: 0, lon: 0 },
      false,
      true
    ).map((tag) => tag.text)

    expect(tags).toEqual(
      expect.arrayContaining([
        'Dans l’établissement scolaire',
        'Partenaire situé à 157 km',
        'Du 23 octobre au 24 octobre 2023 à 22h',
        'Collège - 3e',
      ])
    )

    expect(tagsReduced).toEqual(['Dans l’établissement scolaire'])
  })

  it('should return the list of tags when the offer happens at the offerers location', () => {
    const offer: CollectiveOfferTemplateResponseModel = {
      ...templateOffer,
      offerVenue: {
        ...templateOffer.offerVenue,
        addressType: OfferAddressType.OFFERER_VENUE,
        distance: 100,
      },
      dates: undefined,
    }
    const tags = getOfferTags(offer, { ...adageUser, lat: 0, lon: 0 }).map(
      (tag) => tag.text
    )
    const tagsReduced = getOfferTags(
      offer,
      { ...adageUser, lat: 0, lon: 0 },
      false
    ).map((tag) => tag.text)

    expect(tags).toEqual(
      expect.arrayContaining(['Sortie', 'À 100 km', 'Disponible toute l’année'])
    )

    expect(tagsReduced).toEqual(['Sortie', 'À 100 km'])
  })

  it('should return the list of tags when the offer happens at the offerers location when ff oa is enabled', () => {
    const offer: CollectiveOfferTemplateResponseModel = {
      ...templateOffer,
      location: {
        locationType: CollectiveLocationType.ADDRESS,
        address: {
          isManualEdition: false,
          id_oa: 1,
          id: 1,
          label: 'Le nom du lieu 1',
          city: 'Paris',
          postalCode: '75001',
          latitude: 1,
          longitude: 1,
        },
      },
      dates: undefined,
    }
    const tags = getOfferTags(
      offer,
      { ...adageUser, lat: 0, lon: 0 },
      true,
      true
    ).map((tag) => tag.text)
    const tagsReduced = getOfferTags(
      offer,
      { ...adageUser, lat: 0, lon: 0 },
      false,
      true
    ).map((tag) => tag.text)

    expect(tags).toEqual(
      expect.arrayContaining([
        'Sortie à 157 km',
        'Partenaire situé à 900+ km',
        'Disponible toute l’année',
      ])
    )

    expect(tagsReduced).toEqual(['Sortie à 157 km'])
  })

  it('should return the list of tags when the offer happens at another location', () => {
    const offer: CollectiveOfferTemplateResponseModel = {
      ...templateOffer,
      offerVenue: {
        ...templateOffer.offerVenue,
        addressType: OfferAddressType.OTHER,
      },
      dates: undefined,
    }
    const tags = getOfferTags(offer, { ...adageUser, lat: 10, lon: 10 }).map(
      (tag) => tag.text
    )
    const tagsReduced = getOfferTags(
      offer,
      { ...adageUser, lat: 20, lon: 20 },
      false
    ).map((tag) => tag.text)

    expect(tags).toEqual(
      expect.arrayContaining([
        'Sortie',
        'Lieu à définir',
        'Disponible toute l’année',
        'Partenaire situé à 900+ km',
      ])
    )

    expect(tagsReduced).toEqual(['Sortie', 'Lieu à définir'])
  })

  it('should return the list of tags when the offer happens at another location when ff os is enabled', () => {
    const offer: CollectiveOfferTemplateResponseModel = {
      ...templateOffer,
      location: {
        locationType: CollectiveLocationType.TO_BE_DEFINED,
        locationComment: 'Comment',
      },
      dates: undefined,
    }
    const tags = getOfferTags(
      offer,
      { ...adageUser, lat: 10, lon: 10 },
      true,
      true
    ).map((tag) => tag.text)
    const tagsReduced = getOfferTags(
      offer,
      { ...adageUser, lat: 20, lon: 20 },
      false,
      true
    ).map((tag) => tag.text)

    expect(tags).toEqual(
      expect.arrayContaining([
        'Lieu à déterminer',
        'Partenaire situé à 900+ km',
        'Disponible toute l’année',
      ])
    )

    expect(tagsReduced).toEqual(['Lieu à déterminer'])
  })

  it('should return a multi level tag if there are multiple student levels', () => {
    const offer: CollectiveOfferTemplateResponseModel = {
      ...templateOffer,
      students: [StudentLevels.COLL_GE_3E, StudentLevels.COLL_GE_4E],
    }
    const tags = getOfferTags(offer, adageUser).map((tag) => tag.text)

    expect(tags).toEqual(expect.arrayContaining(['Multiniveaux']))
  })

  it('should return the price and stock tags when the offer is bookable', () => {
    const offer: CollectiveOfferResponseModel = {
      ...bookableOffer,
      stock: {
        ...bookableOffer.stock,
        price: 10000,
        numberOfTickets: 10,
      },
    }
    const tags = getOfferTags(offer, adageUser).map((tag) => tag.text)

    expect(tags).toEqual(expect.arrayContaining(['100,00\xa0€']))
    expect(tags).toEqual(expect.arrayContaining(['10 élèves']))
  })

  it('should return the price as free if the offer is bookable and the price is zero', () => {
    const offer: CollectiveOfferResponseModel = {
      ...bookableOffer,
      stock: {
        ...bookableOffer.stock,
        price: 0,
        numberOfTickets: 10,
      },
    }
    const tags = getOfferTags(offer, adageUser).map((tag) => tag.text)

    expect(tags).toEqual(expect.arrayContaining(['Gratuit']))
  })
})

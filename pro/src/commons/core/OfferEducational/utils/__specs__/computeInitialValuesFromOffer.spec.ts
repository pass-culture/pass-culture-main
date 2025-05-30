import { CollectiveLocationType } from 'apiClient/adage'
import { OfferContactFormEnum } from 'apiClient/v1'
import { getDefaultEducationalValues } from 'commons/core/OfferEducational/constants'
import { formatShortDateForInput } from 'commons/utils/date'
import { getCollectiveOfferTemplateFactory } from 'commons/utils/factories/collectiveApiFactories'
import { venueListItemFactory } from 'commons/utils/factories/individualApiFactories'

import { computeInitialValuesFromOffer } from '../computeInitialValuesFromOffer'

const venueAddress = {
  city: 'Paris',
  id: 1,
  id_oa: 1994,
  latitude: 3,
  longitude: 2,
  isManualEdition: false,
  postalCode: '75018',
  street: 'rue de la paix',
  banId: '',
}

const venues = [
  venueListItemFactory({
    address: venueAddress,
    id: 2,
  }),
]

const offerer = {
  allowedOnAdage: true,
  id: 1,
  managedVenues: venues,
  siren: '123456789',
  name: 'toto',
}

const offerVenue = {
  id: 2,
  managingOfferer: offerer,
  managedVenues: venues,
  name: 'opéra de paris',
}

describe('computeInitialValuesFromOffer', () => {
  it('should return default values when no offer is provided', () => {
    const venue = venues[0]

    expect(computeInitialValuesFromOffer(offerer, false, venues)).toEqual({
      ...getDefaultEducationalValues(),
      offererId: '1',
      venueId: '2',
      city: 'Paris',
      latitude: '3',
      longitude: '2',
      postalCode: '75018',
      street: 'rue de la paix',
      location: {
        locationType: CollectiveLocationType.ADDRESS,
        address: {
          isManualEdition: false,
          isVenueAddress: true,
          id_oa: venue.address?.id_oa.toString(),
          label: 'Le nom du lieu 1',
        },
      },
      contactUrl: undefined,
    })
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

  it('should set location to specific address when offer is located on another address than its venue', () => {
    expect(
      computeInitialValuesFromOffer(
        offerer,
        true,
        venues,
        getCollectiveOfferTemplateFactory({
          location: {
            locationType: CollectiveLocationType.ADDRESS,
            address: {
              label: 'théâtre de savoie',
              id_oa: 1995,
              city: 'Chambéry',
              street: "rue de l'espoir",
              id: 14,
              isManualEdition: false,
              latitude: 12,
              longitude: 3,
              postalCode: '31000',
            },
          },
          venue: offerVenue,
        }),
        undefined,
        false
      )
    ).toEqual(
      expect.objectContaining({
        city: 'Chambéry',
        latitude: '12',
        longitude: '3',
        postalCode: '31000',
        street: "rue de l'espoir",
        location: {
          address: {
            isVenueAddress: false,
            isManualEdition: false,
            id_oa: 'SPECIFIC_ADDRESS',
            label: 'théâtre de savoie',
          },
          locationType: 'ADDRESS',
        },
      })
    )
  })

  it('should set location to venue address when offer is located in its venue', () => {
    expect(
      computeInitialValuesFromOffer(
        offerer,
        true,
        venues,
        getCollectiveOfferTemplateFactory({
          location: {
            locationType: CollectiveLocationType.ADDRESS,
            address: venueAddress,
          },
          venue: offerVenue,
        }),
        undefined,
        false
      )
    ).toEqual(
      expect.objectContaining({
        city: 'Paris',
        latitude: '3',
        longitude: '2',
        postalCode: '75018',
        street: 'rue de la paix',
        location: {
          address: {
            isVenueAddress: true,
            isManualEdition: false,
            id_oa: '1994',
            label: 'Le nom du lieu 1',
          },
          locationType: 'ADDRESS',
        },
      })
    )
  })
})

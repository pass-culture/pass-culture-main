import { computeAddressDisplayName } from 'repository/venuesService'

import { getLocationResponseModel } from '@/commons/utils/factories/commonOffersApiFactories'
import {
  getIndividualOfferFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { OFFER_LOCATION } from '@/pages/IndividualOffer/commons/constants'

import { EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES } from '../../constants'
import { getInitialValuesFromOffer } from '../getInitialValuesFromOffer'

describe('getInitialValuesFromOffer', () => {
  const offerBase = getIndividualOfferFactory()

  const paramsBase = {
    offerVenue: makeVenueListItem({ id: 2 }),
  }

  describe('when offer subcategory is not digital', () => {
    const paramsWithOfflineSubcategory = {
      ...paramsBase,
      isDigital: false,
    }

    describe('when offer has an address', () => {
      it('should include offer address', () => {
        const offer = {
          ...offerBase,
          location: {
            id: 997,
            banId: '35288_7283_00001',
            inseeCode: '89001',
            label: 'Bureau',
            city: 'Paris',
            street: '3 rue de Valois',
            postalCode: '75001',
            isManualEdition: true,
            latitude: 48.85332,
            isVenueLocation: false,
            longitude: 2.348979,
          },
          isDigital: false,
        }

        const addressAutocomplete = computeAddressDisplayName(
          offer.location,
          false
        )

        const result = getInitialValuesFromOffer(
          offer,
          paramsWithOfflineSubcategory
        )

        expect(result).toMatchObject({
          location: {
            'search-addressAutocomplete': addressAutocomplete,
            addressAutocomplete,
            banId: offer.location.banId,
            city: offer.location.city,
            coords: `${offer.location.latitude}, ${offer.location.longitude}`,
            inseeCode: offer.location.inseeCode,
            isManualEdition: offer.location.isManualEdition,
            label: offer.location.label,
            latitude: String(offer.location.latitude),
            longitude: String(offer.location.longitude),
            offerLocation: OFFER_LOCATION.OTHER_ADDRESS,
            postalCode: offer.location.postalCode,
            street: offer.location.street,
          },
          url: null,
        })
      })

      it('should include selected venue OA ID if available', () => {
        const id = 2

        const offer = {
          ...offerBase,
          location: {
            id,
            banId: '35288_7283_00001',
            inseeCode: '89001',
            label: 'Bureau',
            city: 'Paris',
            street: '3 rue de Valois',
            postalCode: '75001',
            isManualEdition: true,
            latitude: 48.85332,
            longitude: 2.348979,
            isVenueLocation: true,
          },
          isDigital: false,
        }
        const params = {
          ...paramsWithOfflineSubcategory,
          offerVenue: makeVenueListItem({
            id: 2,
            location: getLocationResponseModel({
              id,
            }),
          }),
        }

        const result = getInitialValuesFromOffer(offer, params)

        expect(result.location).toEqual(
          expect.objectContaining({
            offerLocation: String(id),
          })
        )
      })
    })

    describe('when offer has NO address', () => {
      const offerWithoutAddress = {
        ...offerBase,
        location: undefined,
      }

      it('should include selected venue address when available', () => {
        const offerVenue = makeVenueListItem({
          id: 2,
          location: getLocationResponseModel(),
        })

        const params = {
          ...paramsWithOfflineSubcategory,
          offerVenue,
        }

        const result = getInitialValuesFromOffer(offerWithoutAddress, params)

        expect(result).toMatchObject({
          location: {
            banId: offerVenue.location.banId,
            city: offerVenue.location.city,
            coords: `${offerVenue.location.latitude}, ${offerVenue.location.longitude}`,
            inseeCode: offerVenue.location.inseeCode,
            label: offerVenue.location.label,
            latitude: String(offerVenue.location.latitude),
            longitude: String(offerVenue.location.longitude),
            offerLocation: String(offerVenue.location.id),
            postalCode: offerVenue.location.postalCode,
            street: offerVenue.location.street,
          },
          url: null,
        })
      })

      it('should handle missing address props in selected venue', () => {
        const offerVenue = makeVenueListItem({
          id: 2,
          location: getLocationResponseModel({
            banId: undefined,
            inseeCode: undefined,
            label: undefined,
            street: undefined,
          }),
        })

        const params = {
          ...paramsWithOfflineSubcategory,
          offerVenue,
        }

        const result = getInitialValuesFromOffer(offerWithoutAddress, params)

        expect(result).toMatchObject({
          location: {
            banId: null,
            inseeCode: null,
            label: null,
            street: null,
          },
        })
      })
    })

    it('should accept any url format when offline', () => {
      const offerVenue = makeVenueListItem({
        id: 2,
        location: getLocationResponseModel(),
      })
      const params = { ...paramsWithOfflineSubcategory, offerVenue }

      const result = getInitialValuesFromOffer(
        { ...offerBase, location: undefined, url: 'not-a-url' },
        params
      )

      expect(result.url).toBe('not-a-url')
    })
  })

  it('should NOT include offer address when the offer is digital', () => {
    const mockOfferWithAddress = {
      ...offerBase,
      location: {
        id: 997,
        banId: '35288_7283_00001',
        inseeCode: '89001',
        label: 'Bureau',
        city: 'Paris',
        street: '3 rue de Valois',
        postalCode: '75001',
        isManualEdition: true,
        latitude: 48.85332,
        longitude: 2.348979,
        isVenueLocation: false,
      },
      url: 'https://passculture.app',
      isDigital: true,
    }

    const result = getInitialValuesFromOffer(mockOfferWithAddress, paramsBase)

    expect(result).toMatchObject({
      location: null,
      url: 'https://passculture.app',
    })
  })

  it('should return EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES when neither offer nor venue has address (offline)', () => {
    const offer = { ...offerBase, location: undefined }
    const params = {
      offerVenue: makeVenueListItem({
        id: 2,
        location: undefined,
      }),
      isDigital: false,
    }

    const result = getInitialValuesFromOffer(offer, params)

    expect(result.location).toEqual(EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES)
  })
})

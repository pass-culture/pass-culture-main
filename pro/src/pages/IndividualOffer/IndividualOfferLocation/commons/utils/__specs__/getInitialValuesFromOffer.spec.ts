import { computeAddressDisplayName } from '@/commons/format/venuesService'
import { getLocationResponseModelV2 } from '@/commons/utils/factories/commonOffersApiFactories'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { OFFER_LOCATION } from '@/pages/IndividualOffer/commons/constants'

import { getInitialValuesFromOffer } from '../getInitialValuesFromOffer'

describe('getInitialValuesFromOffer', () => {
  const offerBase = getIndividualOfferFactory()

  const paramsBase = {
    offerVenue: makeGetVenueResponseModel({ id: 2 }),
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
            departmentCode: '89',
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
            departmentCode: '75',
          },
          isDigital: false,
        }
        const params = {
          ...paramsWithOfflineSubcategory,
          offerVenue: makeGetVenueResponseModel({
            id: 2,
            location: getLocationResponseModelV2({
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
        location: null,
      }

      it('should include selected venue address when available', () => {
        const offerVenue = makeGetVenueResponseModel({
          id: 2,
          location: getLocationResponseModelV2(),
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
        const offerVenue = makeGetVenueResponseModel({
          id: 2,
          location: getLocationResponseModelV2({
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
      const offerVenue = makeGetVenueResponseModel({
        id: 2,
        location: getLocationResponseModelV2(),
      })
      const params = { ...paramsWithOfflineSubcategory, offerVenue }

      const result = getInitialValuesFromOffer(
        { ...offerBase, location: null, url: 'not-a-url' },
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
        departmentCode: '89',
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
})

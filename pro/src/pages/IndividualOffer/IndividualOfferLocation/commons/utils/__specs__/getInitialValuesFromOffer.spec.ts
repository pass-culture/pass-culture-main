import { computeAddressDisplayName } from 'repository/venuesService'

import { getAddressResponseIsLinkedToVenueModelFactory } from '@/commons/utils/factories/commonOffersApiFactories'
import {
  getIndividualOfferFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { OFFER_LOCATION } from '@/pages/IndividualOffer/commons/constants'

import { getInitialValuesFromOffer } from '../getInitialValuesFromOffer'

describe('getInitialValuesFromOffer', () => {
  const offerBase = getIndividualOfferFactory()

  const paramsBase = {
    offerVenue: makeVenueListItem({}),
  }

  describe('when offer subcategory is offline', () => {
    const paramsWithOfflineSubcategory = {
      ...paramsBase,
      isOfferSubcategoryOnline: false,
    }

    describe('when offer has an address', () => {
      it('should include offer address', () => {
        const offer = {
          ...offerBase,
          address: {
            id: 1,
            id_oa: 997,
            banId: '35288_7283_00001',
            inseeCode: '89001',
            label: 'Bureau',
            city: 'Paris',
            street: '3 rue de Valois',
            postalCode: '75001',
            isManualEdition: true,
            latitude: 48.85332,
            longitude: 2.348979,
          },
        }

        const addressAutocomplete = computeAddressDisplayName(
          offer.address,
          false
        )

        const result = getInitialValuesFromOffer(
          offer,
          paramsWithOfflineSubcategory
        )

        expect(result).toMatchObject({
          'search-addressAutocomplete': addressAutocomplete,
          addressAutocomplete,
          banId: offer.address.banId,
          city: offer.address.city,
          coords: `${offer.address.latitude}, ${offer.address.longitude}`,
          inseeCode: offer.address.inseeCode,
          latitude: String(offer.address.latitude),
          locationLabel: offer.address.label,
          longitude: String(offer.address.longitude),
          isManualEdition: offer.address.isManualEdition,
          offerLocation: OFFER_LOCATION.OTHER_ADDRESS,
          postalCode: offer.address.postalCode,
          street: offer.address.street,
          url: null,
        })
      })

      it('should include selected venue OA ID if available', () => {
        const id_oa = 2

        const offer = {
          ...offerBase,
          address: {
            id: 1,
            id_oa,
            banId: '35288_7283_00001',
            inseeCode: '89001',
            label: 'Bureau',
            city: 'Paris',
            street: '3 rue de Valois',
            postalCode: '75001',
            isManualEdition: true,
            latitude: 48.85332,
            longitude: 2.348979,
          },
        }
        const params = {
          ...paramsWithOfflineSubcategory,
          offerVenue: makeVenueListItem({
            address: getAddressResponseIsLinkedToVenueModelFactory({
              id_oa,
            }),
          }),
        }

        const result = getInitialValuesFromOffer(offer, params)

        expect(result).toEqual(
          expect.objectContaining({
            offerLocation: String(id_oa),
          })
        )
      })
    })

    describe('when offer has NO address', () => {
      const offerWithoutAddress = {
        ...offerBase,
        address: undefined,
      }

      it('should include selected venue address when available', () => {
        const offerVenue = makeVenueListItem({
          address: getAddressResponseIsLinkedToVenueModelFactory(),
        })

        const params = {
          ...paramsWithOfflineSubcategory,
          offerVenue,
        }

        const result = getInitialValuesFromOffer(offerWithoutAddress, params)

        expect(result).toMatchObject({
          banId: offerVenue.address.banId,
          city: offerVenue.address.city,
          coords: `${offerVenue.address.latitude}, ${offerVenue.address.longitude}`,
          inseeCode: offerVenue.address.inseeCode,
          latitude: String(offerVenue.address.latitude),
          locationLabel: offerVenue.address.label,
          longitude: String(offerVenue.address.longitude),
          offerLocation: String(offerVenue.address.id_oa),
          postalCode: offerVenue.address.postalCode,
          street: offerVenue.address.street,
          url: null,
        })
      })

      it('should handle missing address props in selected venue', () => {
        const offerVenue = makeVenueListItem({
          address: getAddressResponseIsLinkedToVenueModelFactory({
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
          banId: null,
          inseeCode: null,
          locationLabel: null,
          street: null,
        })
      })
    })

    it('should accept any url format when offline', () => {
      const offerVenue = makeVenueListItem({
        address: getAddressResponseIsLinkedToVenueModelFactory(),
      })
      const params = { ...paramsWithOfflineSubcategory, offerVenue }

      const result = getInitialValuesFromOffer(
        { ...offerBase, address: undefined, url: 'not-a-url' },
        params
      )

      expect(result.url).toBe('not-a-url')
    })
  })

  describe('when offer subcategory is online', () => {
    const paramsWithOnlineSubcategory = {
      ...paramsBase,
      isOfferSubcategoryOnline: true,
    }

    it('should NOT include offer address', () => {
      const mockOfferWithAddress = {
        ...offerBase,
        address: {
          id: 1,
          id_oa: 997,
          banId: '35288_7283_00001',
          inseeCode: '89001',
          label: 'Bureau',
          city: 'Paris',
          street: '3 rue de Valois',
          postalCode: '75001',
          isManualEdition: true,
          latitude: 48.85332,
          longitude: 2.348979,
        },
        url: 'https://passculture.app',
      }

      const result = getInitialValuesFromOffer(
        mockOfferWithAddress,
        paramsWithOnlineSubcategory
      )

      expect(result).toMatchObject({
        addressAutocomplete: null,
        banId: null,
        city: null,
        coords: null,
        inseeCode: null,
        latitude: null,
        locationLabel: null,
        longitude: null,
        isManualEdition: false,
        offerLocation: null,
        postalCode: null,
        'search-addressAutocomplete': null,
        street: null,
        url: 'https://passculture.app',
      })
    })

    it('should include a valid url when online', () => {
      const result = getInitialValuesFromOffer(
        { ...offerBase, url: 'https://passculture.app' },
        paramsWithOnlineSubcategory
      )
      expect(result.url).toBe('https://passculture.app')
    })
  })
})

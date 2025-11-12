import { computeAddressDisplayName } from 'repository/venuesService'

import { getAddressResponseIsLinkedToVenueModelFactory } from '@/commons/utils/factories/commonOffersApiFactories'
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
          isDigital: false,
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
          address: {
            'search-addressAutocomplete': addressAutocomplete,
            addressAutocomplete,
            banId: offer.address.banId,
            city: offer.address.city,
            coords: `${offer.address.latitude}, ${offer.address.longitude}`,
            inseeCode: offer.address.inseeCode,
            isManualEdition: offer.address.isManualEdition,
            label: offer.address.label,
            latitude: String(offer.address.latitude),
            longitude: String(offer.address.longitude),
            offerLocation: OFFER_LOCATION.OTHER_ADDRESS,
            postalCode: offer.address.postalCode,
            street: offer.address.street,
          },
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
          isDigital: false,
        }
        const params = {
          ...paramsWithOfflineSubcategory,
          offerVenue: makeVenueListItem({
            id: 2,
            address: getAddressResponseIsLinkedToVenueModelFactory({
              id_oa,
            }),
          }),
        }

        const result = getInitialValuesFromOffer(offer, params)

        expect(result.address).toEqual(
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
          id: 2,
          address: getAddressResponseIsLinkedToVenueModelFactory(),
        })

        const params = {
          ...paramsWithOfflineSubcategory,
          offerVenue,
        }

        const result = getInitialValuesFromOffer(offerWithoutAddress, params)

        expect(result).toMatchObject({
          address: {
            banId: offerVenue.address.banId,
            city: offerVenue.address.city,
            coords: `${offerVenue.address.latitude}, ${offerVenue.address.longitude}`,
            inseeCode: offerVenue.address.inseeCode,
            label: offerVenue.address.label,
            latitude: String(offerVenue.address.latitude),
            longitude: String(offerVenue.address.longitude),
            offerLocation: String(offerVenue.address.id_oa),
            postalCode: offerVenue.address.postalCode,
            street: offerVenue.address.street,
          },
          url: null,
        })
      })

      it('should handle missing address props in selected venue', () => {
        const offerVenue = makeVenueListItem({
          id: 2,
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
          address: {
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

  it('should NOT include offer address when the offer is digital', () => {
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
      isDigital: true,
    }

    const result = getInitialValuesFromOffer(mockOfferWithAddress, paramsBase)

    expect(result).toMatchObject({
      address: null,
      url: 'https://passculture.app',
    })
  })

  it('should return EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES when neither offer nor venue has address (offline)', () => {
    const offer = { ...offerBase, address: undefined }
    const params = {
      offerVenue: makeVenueListItem({
        id: 2,
        address: undefined,
      }),
      isDigital: false,
    }

    const result = getInitialValuesFromOffer(offer, params)

    expect(result.address).toEqual(EMPTY_PHYSICAL_ADDRESS_SUBFORM_VALUES)
  })
})

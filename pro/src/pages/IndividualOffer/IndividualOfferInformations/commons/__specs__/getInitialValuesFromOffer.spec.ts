import { computeAddressDisplayName } from 'repository/venuesService'

import {
  GetIndividualOfferWithAddressResponseModel,
  VenueListItemResponseModel,
  WithdrawalTypeEnum,
} from '@/apiClient/v1'
import { AccessibilityEnum } from '@/commons/core/shared/types'
import { getAddressResponseIsLinkedToVenueModelFactory } from '@/commons/utils/factories/commonOffersApiFactories'
import {
  getIndividualOfferFactory,
  subcategoryFactory,
  venueListItemFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { OFFER_LOCATION } from '@/pages/IndividualOffer/commons/constants'

import { DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES } from '../constants'
import { getInitialValuesFromOffer } from '../getInitialValuesFromOffer'

const mockOffer: GetIndividualOfferWithAddressResponseModel =
  getIndividualOfferFactory({
    isEvent: true,
    isNational: false,
    withdrawalDetails: 'Detailed info',
    withdrawalDelay: 3,
    withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
    visualDisabilityCompliant: true,
    mentalDisabilityCompliant: false,
    audioDisabilityCompliant: true,
    motorDisabilityCompliant: false,
    bookingEmail: 'test@example.com',
    bookingContact: 'Contact Info',
    externalTicketOfficeUrl: 'https://hello.co',
    url: 'http://example.com',
  })

describe('getInitialValuesFromOffer', () => {
  describe.each([
    { isNewOfferCreationFlowFeatureActive: false },
    { isNewOfferCreationFlowFeatureActive: true },
  ])(
    'with isNewOfferCreationFlowFeatureActive = $isNewOfferCreationFlowFeatureActive (both)',
    ({ isNewOfferCreationFlowFeatureActive }) => {
      const paramsBase = {
        isNewOfferCreationFlowFeatureActive,
        isOfferSubcategoryOnline: false,
        offerSubcategory: subcategoryFactory(),
        offerVenue: venueListItemFactory(),
      }

      it('should return default initial values completed with offer values when provided', () => {
        const result = getInitialValuesFromOffer(mockOffer, paramsBase)

        expect(result).toEqual(
          expect.objectContaining({
            isEvent: mockOffer.isEvent,
            isNational: mockOffer.isNational,
            withdrawalDetails: mockOffer.withdrawalDetails,
            withdrawalDelay: mockOffer.withdrawalDelay?.toString(),
            withdrawalType: mockOffer.withdrawalType,
            bookingEmail: mockOffer.bookingEmail,
            bookingContact: mockOffer.bookingContact,
            externalTicketOfficeUrl: mockOffer.externalTicketOfficeUrl,
          })
        )
      })

      it('should handle missing properties when offer is provided', () => {
        const mockOfferWithMissingProperties: GetIndividualOfferWithAddressResponseModel =
          {
            ...mockOffer,
            withdrawalDetails: undefined,
            withdrawalDelay: undefined,
            withdrawalType: undefined,
            bookingEmail: undefined,
            bookingContact: undefined,
            externalTicketOfficeUrl: undefined,
          }

        const result = getInitialValuesFromOffer(
          mockOfferWithMissingProperties,
          paramsBase
        )

        expect(result).toEqual(
          expect.objectContaining({
            withdrawalDetails:
              DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES.withdrawalDetails,
            withdrawalDelay: undefined,
            withdrawalType: undefined,
            bookingEmail: '',
            bookingContact: undefined,
            receiveNotificationEmails: false,
            externalTicketOfficeUrl: undefined,
          })
        )
      })

      it('should handle null withdrawalDelay correctly', () => {
        const mockOfferWithNullWithdrawalDelay: GetIndividualOfferWithAddressResponseModel =
          {
            ...mockOffer,
            withdrawalDelay: null,
          }

        const result = getInitialValuesFromOffer(
          mockOfferWithNullWithdrawalDelay,
          paramsBase
        )

        expect(result).toEqual(
          expect.objectContaining({
            withdrawalDelay: undefined,
          })
        )
      })

      describe('when offer has address properties', () => {
        it('should return default initial values completed with offer address values', () => {
          const mockOfferWithAddress: GetIndividualOfferWithAddressResponseModel =
            {
              ...mockOffer,
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
            mockOfferWithAddress.address!,
            false
          )

          const result = getInitialValuesFromOffer(
            mockOfferWithAddress,
            paramsBase
          )

          expect(result).toEqual(
            expect.objectContaining({
              offerLocation: OFFER_LOCATION.OTHER_ADDRESS,
              manuallySetAddress: mockOfferWithAddress.address?.isManualEdition,
              'search-addressAutocomplete': addressAutocomplete,
              addressAutocomplete,
              coords: `${mockOfferWithAddress.address?.latitude}, ${mockOfferWithAddress.address?.longitude}`,
              banId: mockOfferWithAddress.address?.banId,
              inseeCode: mockOfferWithAddress.address?.inseeCode,
              locationLabel: mockOfferWithAddress.address?.label,
              street: mockOfferWithAddress.address?.street,
              postalCode: mockOfferWithAddress.address?.postalCode,
              city: mockOfferWithAddress.address?.city,
              latitude: String(mockOfferWithAddress.address?.latitude),
              longitude: String(mockOfferWithAddress.address?.longitude),
            })
          )
        })

        it('should handle missing address properties', () => {
          const mockOfferWithPartialAddress: GetIndividualOfferWithAddressResponseModel =
            {
              ...mockOffer,
              address: {
                id: 1,
                id_oa: 997,
                banId: undefined,
                inseeCode: undefined,
                label: undefined,
                city: 'Paris',
                street: undefined,
                postalCode: '75001',
                isManualEdition: true,
                latitude: 48.85332,
                longitude: 2.348979,
              },
            }

          const result = getInitialValuesFromOffer(
            mockOfferWithPartialAddress,
            paramsBase
          )

          expect(result).toEqual(
            expect.objectContaining({
              banId: '',
              inseeCode: '',
              locationLabel: '',
              street: '',
            })
          )
        })

        it('should use OA id from selected venue if available', () => {
          const mockOfferWithVenueAddress: GetIndividualOfferWithAddressResponseModel =
            {
              ...mockOffer,
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

          const result = getInitialValuesFromOffer(mockOfferWithVenueAddress, {
            ...paramsBase,
            offerVenue: venueListItemFactory({
              address: getAddressResponseIsLinkedToVenueModelFactory({
                id_oa: mockOfferWithVenueAddress.address?.id_oa,
              }),
            }),
          })

          expect(result).toEqual(
            expect.objectContaining({
              offerLocation: String(mockOfferWithVenueAddress.address?.id_oa),
            })
          )
        })
      })

      describe('when non-digital offer has no address properties but a venue is selected', () => {
        it('should return default initial values completed with selected venue address values', () => {
          const mockOfferNonDigitalWithoutAddress: GetIndividualOfferWithAddressResponseModel =
            {
              ...mockOffer,
              isDigital: false,
              address: undefined,
            }
          const offerVenue: VenueListItemResponseModel = venueListItemFactory({
            address: getAddressResponseIsLinkedToVenueModelFactory(),
          })

          const expectedValues = {
            offerLocation: String(offerVenue.address?.id_oa),
            coords: `${offerVenue.address?.latitude}, ${offerVenue.address?.longitude}`,
            banId: offerVenue.address?.banId,
            inseeCode: offerVenue.address?.inseeCode,
            locationLabel: offerVenue.address?.label,
            street: offerVenue.address?.street,
            postalCode: offerVenue.address?.postalCode,
            city: offerVenue.address?.city,
            latitude: String(offerVenue.address?.latitude),
            longitude: String(offerVenue.address?.longitude),
          }

          const result = getInitialValuesFromOffer(
            mockOfferNonDigitalWithoutAddress,
            {
              ...paramsBase,
              offerVenue: offerVenue,
            }
          )

          expect(result).toEqual(expect.objectContaining(expectedValues))
        })

        it('should handle missing address properties in selected venue', () => {
          const mockOfferNonDigitalWithoutAddress: GetIndividualOfferWithAddressResponseModel =
            {
              ...mockOffer,
              isDigital: false,
              address: undefined,
            }
          const offerVenue: VenueListItemResponseModel = venueListItemFactory({
            address: getAddressResponseIsLinkedToVenueModelFactory({
              banId: undefined,
              inseeCode: undefined,
              label: undefined,
              street: undefined,
            }),
          })

          const expectedValues = {
            banId: '',
            inseeCode: '',
            locationLabel: '',
            street: '',
          }

          const result = getInitialValuesFromOffer(
            mockOfferNonDigitalWithoutAddress,
            {
              ...paramsBase,
              offerVenue: offerVenue,
            }
          )

          expect(result).toEqual(expect.objectContaining(expectedValues))
        })
      })

      describe('withdrawalType logic', () => {
        it('should be set to NO_TICKET if offer withdrawalType is missing and subcategory can be withdrawable', () => {
          const offerWithoutWithdrawalType = {
            ...mockOffer,
            withdrawalType: undefined,
          }

          const result = getInitialValuesFromOffer(offerWithoutWithdrawalType, {
            ...paramsBase,
            offerSubcategory: subcategoryFactory({ canBeWithdrawable: true }),
          })

          expect(result.withdrawalType).toBe(WithdrawalTypeEnum.NO_TICKET)
        })

        it('should be undefined if offer withdrawalType is missing and subcategory cannot be withdrawable', () => {
          const offerWithoutWithdrawalType = {
            ...mockOffer,
            withdrawalType: undefined,
          }

          const result = getInitialValuesFromOffer(offerWithoutWithdrawalType, {
            ...paramsBase,
            offerSubcategory: subcategoryFactory({ canBeWithdrawable: false }),
          })

          expect(result.withdrawalType).toBeUndefined()
        })
      })
    }
  )

  describe('with isNewOfferCreationFlowFeatureActive = true', () => {
    const paramsBase = {
      isNewOfferCreationFlowFeatureActive: true,
      offerSubcategory: subcategoryFactory(),
      offerVenue: venueListItemFactory(),
    }

    it('should not include address fields if offer subcategory is online', () => {
      const mockOfferWithAddress: GetIndividualOfferWithAddressResponseModel = {
        ...mockOffer,
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

      const result = getInitialValuesFromOffer(mockOfferWithAddress, {
        ...paramsBase,
        isOfferSubcategoryOnline: true,
      })

      expect(result.offerLocation).toBeUndefined()
      expect(result.addressAutocomplete).toBeUndefined()
      expect(result.coords).toBeUndefined()
      expect(result.street).toBeUndefined()
    })
  })

  describe('with isNewOfferCreationFlowFeatureActive = false', () => {
    const paramsBase = {
      isNewOfferCreationFlowFeatureActive: false,
      isOfferSubcategoryOnline: false,
      offerSubcategory: subcategoryFactory(),
      offerVenue: venueListItemFactory(),
    }

    it('should handle accessibility properties all being set to false', () => {
      const mockOfferWithAllAccessibilityFalse: GetIndividualOfferWithAddressResponseModel =
        {
          ...mockOffer,
          visualDisabilityCompliant: false,
          mentalDisabilityCompliant: false,
          audioDisabilityCompliant: false,
          motorDisabilityCompliant: false,
        }

      const expectedValues = {
        accessibility: {
          [AccessibilityEnum.VISUAL]: false,
          [AccessibilityEnum.MENTAL]: false,
          [AccessibilityEnum.AUDIO]: false,
          [AccessibilityEnum.MOTOR]: false,
          [AccessibilityEnum.NONE]: true, // Since all are false, NONE should be true
        },
      }

      const result = getInitialValuesFromOffer(
        mockOfferWithAllAccessibilityFalse,
        paramsBase
      )

      expect(result).toEqual(expect.objectContaining(expectedValues))
    })

    it('should handle accessibility properties not being set', () => {
      const mockOfferWithMissingProperties: GetIndividualOfferWithAddressResponseModel =
        {
          ...mockOffer,
          visualDisabilityCompliant: undefined,
          mentalDisabilityCompliant: undefined,
          audioDisabilityCompliant: undefined,
          motorDisabilityCompliant: undefined,
        }

      const expectedValues = {
        accessibility: {
          [AccessibilityEnum.VISUAL]: false,
          [AccessibilityEnum.MENTAL]: false,
          [AccessibilityEnum.AUDIO]: false,
          [AccessibilityEnum.MOTOR]: false,
          [AccessibilityEnum.NONE]: true,
        },
      }

      const result = getInitialValuesFromOffer(
        mockOfferWithMissingProperties,
        paramsBase
      )

      expect(result).toEqual(expect.objectContaining(expectedValues))
    })
  })
})

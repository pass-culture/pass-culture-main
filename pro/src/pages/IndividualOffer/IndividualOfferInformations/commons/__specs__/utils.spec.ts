import { computeAddressDisplayName } from 'repository/venuesService'

import {
  GetIndividualOfferWithAddressResponseModel,
  OfferStatus,
  VenueListItemResponseModel,
  WithdrawalTypeEnum,
} from '@/apiClient//v1'
import { AccessibilityEnum } from '@/commons/core/shared/types'
import { getAddressResponseIsLinkedToVenueModelFactory } from '@/commons/utils/factories/commonOffersApiFactories'
import {
  getIndividualOfferFactory,
  venueListItemFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { OFFER_LOCATION } from '@/pages/IndividualOffer/commons/constants'

import { DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES } from '../constants'
import { getFormReadOnlyFields, getInitialValuesFromOffer } from '../utils'

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
      it('should return default initial values completed with offer values when provided', () => {
        const expectedValues = {
          isEvent: mockOffer.isEvent,
          isNational: mockOffer.isNational,
          withdrawalDetails: mockOffer.withdrawalDetails,
          withdrawalDelay: mockOffer.withdrawalDelay?.toString(),
          withdrawalType: mockOffer.withdrawalType,
          bookingEmail: mockOffer.bookingEmail,
          bookingContact: mockOffer.bookingContact,
          externalTicketOfficeUrl: mockOffer.externalTicketOfficeUrl,
        }
        const result = getInitialValuesFromOffer(mockOffer, {
          isNewOfferCreationFlowFeatureActive,
        })

        expect(result).toEqual(expect.objectContaining(expectedValues))
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

        const expectedValues = {
          withdrawalDetails:
            DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES.withdrawalDetails,
          withdrawalDelay: undefined,
          withdrawalType: undefined,
          bookingEmail: '',
          bookingContact: undefined,
          receiveNotificationEmails: false,
          externalTicketOfficeUrl: undefined,
        }

        const result = getInitialValuesFromOffer(
          mockOfferWithMissingProperties,
          {
            isNewOfferCreationFlowFeatureActive,
          }
        )

        expect(result).toEqual(expect.objectContaining(expectedValues))
      })

      it('should handle null withdrawalDelay correctly', () => {
        const mockOfferWithNullWithdrawalDelay: GetIndividualOfferWithAddressResponseModel =
          {
            ...mockOffer,
            withdrawalDelay: null,
          }

        const expectedValues = {
          withdrawalDelay: undefined,
        }

        const result = getInitialValuesFromOffer(
          mockOfferWithNullWithdrawalDelay,
          {
            isNewOfferCreationFlowFeatureActive,
          }
        )

        expect(result).toEqual(expect.objectContaining(expectedValues))
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

          const expectedValues = {
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
          }

          const result = getInitialValuesFromOffer(mockOfferWithAddress, {
            isNewOfferCreationFlowFeatureActive,
          })

          expect(result).toEqual(expect.objectContaining(expectedValues))
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

          const expectedValues = {
            banId: '',
            inseeCode: '',
            locationLabel: '',
            street: '',
          }

          const result = getInitialValuesFromOffer(
            mockOfferWithPartialAddress,
            {
              isNewOfferCreationFlowFeatureActive,
            }
          )

          expect(result).toEqual(expect.objectContaining(expectedValues))
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

          const expectedValues = {
            offerLocation: String(mockOfferWithVenueAddress.address?.id_oa),
          }

          const result = getInitialValuesFromOffer(mockOfferWithVenueAddress, {
            isNewOfferCreationFlowFeatureActive,
            selectedVenue: venueListItemFactory({
              address: getAddressResponseIsLinkedToVenueModelFactory({
                id_oa: mockOfferWithVenueAddress.address?.id_oa,
              }),
            }),
          })

          expect(result).toEqual(expect.objectContaining(expectedValues))
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
          const selectedVenue: VenueListItemResponseModel =
            venueListItemFactory({
              address: getAddressResponseIsLinkedToVenueModelFactory(),
            })

          const expectedValues = {
            offerLocation: String(selectedVenue.address?.id_oa),
            coords: `${selectedVenue.address?.latitude}, ${selectedVenue.address?.longitude}`,
            banId: selectedVenue.address?.banId,
            inseeCode: selectedVenue.address?.inseeCode,
            locationLabel: selectedVenue.address?.label,
            street: selectedVenue.address?.street,
            postalCode: selectedVenue.address?.postalCode,
            city: selectedVenue.address?.city,
            latitude: String(selectedVenue.address?.latitude),
            longitude: String(selectedVenue.address?.longitude),
          }

          const result = getInitialValuesFromOffer(
            mockOfferNonDigitalWithoutAddress,
            {
              isNewOfferCreationFlowFeatureActive,
              selectedVenue,
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
          const selectedVenue: VenueListItemResponseModel =
            venueListItemFactory({
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
              isNewOfferCreationFlowFeatureActive,
              selectedVenue,
            }
          )

          expect(result).toEqual(expect.objectContaining(expectedValues))
        })
      })
    }
  )

  describe('with isNewOfferCreationFlowFeatureActive = false', () => {
    const isNewOfferCreationFlowFeatureActive = false

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
        {
          isNewOfferCreationFlowFeatureActive,
        }
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

      const result = getInitialValuesFromOffer(mockOfferWithMissingProperties, {
        isNewOfferCreationFlowFeatureActive,
      })

      expect(result).toEqual(expect.objectContaining(expectedValues))
    })
  })
})

describe('getFormReadOnlyFields', () => {
  it('should return all fields as read only when offer is rejected', () => {
    const offer = getIndividualOfferFactory({
      status: OfferStatus.REJECTED,
    })

    const result = getFormReadOnlyFields(offer)

    expect(result).toEqual(
      Object.keys(DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES)
    )
  })

  it('should return all fields as read only when offer is pending', () => {
    const offer = getIndividualOfferFactory({
      status: OfferStatus.PENDING,
    })

    const result = getFormReadOnlyFields(offer)

    expect(result).toEqual(
      Object.keys(DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES)
    )
  })

  it('should return some fields as not read only when offer is synchronized', () => {
    const offer = getIndividualOfferFactory({
      lastProvider: { name: 'Allocine' },
    })

    const result = getFormReadOnlyFields(offer)

    expect(result).not.toContain(['accessibility'])
  })
})

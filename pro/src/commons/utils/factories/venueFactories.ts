import type {
  GetOfferVenueResponseModel,
  GetVenueAddressResponseModel,
  GetVenueManagingOffererResponseModel,
  GetVenueResponseModel,
  LocationResponseModelV2,
  VenueListItemLiteResponseModel,
  VenueTypeResponseModelV2,
} from '@/apiClient/v1'

import type { PartialExcept } from '../types'

let VENUE_ID = 0

export const offerVenueFactory = (
  customOfferVenue: Partial<GetOfferVenueResponseModel> = {}
): GetOfferVenueResponseModel => {
  const id = customOfferVenue.id ?? VENUE_ID++

  return {
    id,
    audioDisabilityCompliant: true,
    isVirtual: false,
    managingOfferer: {
      id: 1,
      name: 'Le nom de l’offreur 1',
    },
    mentalDisabilityCompliant: true,
    motorDisabilityCompliant: true,
    name: `Nom de la structure ${id}`,
    publicName: `Nom public de la structure ${id}`,
    visualDisabilityCompliant: true,
    ...customOfferVenue,
  }
}

export const makeGetVenueManagingOffererResponseModel = <
  T extends PartialExcept<GetVenueManagingOffererResponseModel, 'id'>,
>(
  override: T
): Omit<GetVenueManagingOffererResponseModel, keyof T> & T => {
  const fake: GetVenueManagingOffererResponseModel = {
    id: override.id,
    isValidated: false,
    name: `Entité ${override.id}`,
    siren: '123456789',
  }

  return {
    ...fake,
    ...override,
  }
}

export const makeGetVenueResponseModel = <
  T extends PartialExcept<GetVenueResponseModel, 'id'>,
>(
  override: T
): Omit<GetVenueResponseModel, keyof T> & T => {
  const offererId = override.managingOfferer?.id ?? 1
  const offererName = override.managingOfferer?.name ?? `Entité ${offererId}`
  const offerer =
    override.managingOfferer ??
    makeGetVenueManagingOffererResponseModel({
      id: offererId,
      name: offererName,
    })

  const fake: GetVenueResponseModel = {
    id: override.id,
    activity: null,
    allowedOnAdage: false,
    audioDisabilityCompliant: false,
    adageInscriptionDate: null,
    bankAccountStatus: null,
    bannerMeta: null,
    bannerUrl: null,
    bookingEmail: `booking.${override.id}@test.com`,
    collectiveAccessInformation: null,
    collectiveDescription: null,
    collectiveDmsApplications: [],
    collectiveDomains: [],
    collectiveEmail: null,
    collectiveInterventionArea: null,
    collectiveLegalStatus: null,
    collectiveNetwork: null,
    collectivePhone: null,
    collectiveStudents: null,
    collectiveWebsite: null,
    comment: null,
    contact: null,
    dateCreated: new Date().toISOString(),
    description: 'description',
    externalAccessibilityData: null,
    externalAccessibilityId: null,
    externalAccessibilityUrl: null,
    hasActiveIndividualOffer: false,
    hasAdageId: false,
    hasOffers: false,
    hasNonFreeOffers: false,
    hasPartnerPage: false,
    isActive: false,
    isCaledonian: false,
    isOpenToPublic: false,
    isPermanent: false,
    isValidated: false,
    isVirtual: false,
    location: null,
    managingOfferer: offerer,
    mentalDisabilityCompliant: false,
    motorDisabilityCompliant: false,
    name: `Nom de la structure ${override.id}`,
    openingHours: null,
    publicName: `Nom public de la structure ${override.id}`,
    pricingPoint: null,
    siret: null,
    venueType: makeVenueTypeResponseModel({}),
    visualDisabilityCompliant: false,
    canDisplayHighlights: false,
    hasNonDraftOffers: false,
    volunteeringUrl: null,
    withdrawalDetails: null,
  }

  return {
    ...fake,
    ...override,
  }
}

const makeVenueTypeResponseModel = <
  T extends Partial<VenueTypeResponseModelV2>,
>(
  override: T
): Omit<VenueTypeResponseModelV2, keyof T> & T => {
  const fake: VenueTypeResponseModelV2 = {
    label: 'Autre',
    // Auto-generated `VenueTypeCode` enum is completely wrong:
    // real keys are those declared in api/src/pcapi/core/offerers/schemas.py
    value: 'OTHER',
  }

  return {
    ...fake,
    ...override,
  }
}

let venueAddressId = 1

export const venueAddressFactory = (
  venueId: number,
  customVenueAddress: Partial<GetVenueAddressResponseModel> = {}
): GetVenueAddressResponseModel => {
  const currentOaId = venueAddressId++

  return {
    venueId: venueId,
    addressId: currentOaId,
    id: currentOaId,
    label: 'ma venue',
    city: 'Paris',
    postalCode: '75001',
    street: '1 Rue de paris',
    departmentCode: '75',
    venueName: 'some venue',
    ...customVenueAddress,
  }
}

export const makeVenueListItemLiteResponseModel = <
  T extends PartialExcept<VenueListItemLiteResponseModel, 'id'>,
>(
  override: T
): Omit<VenueListItemLiteResponseModel, keyof T> & T => {
  const offererId = override.managingOffererId ?? 1
  const location: LocationResponseModelV2 = {
    id: 2,
    banId: null,
    city: 'Paris',
    departmentCode: null,
    inseeCode: null,
    isManualEdition: false,
    isVenueLocation: false,
    label: null,
    latitude: 0,
    longitude: 0,
    postalCode: '75001',
    street: null,
  }

  const fake: VenueListItemLiteResponseModel = {
    id: override.id,
    location,
    managingOffererId: offererId,
    publicName: `Nom public de la structure ${override.id}`,
  }

  return {
    ...fake,
    ...override,
  }
}

/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ExternalAccessibilityDataModelV2 } from './ExternalAccessibilityDataModelV2';
import type { LocationResponseModelV2 } from './LocationResponseModelV2';
import type { SimplifiedBankAccountStatus } from './SimplifiedBankAccountStatus';
import type { VenueTypeCodeKey } from './VenueTypeCodeKey';
export type VenueListItemResponseModel = {
  audioDisabilityCompliant: (boolean | null);
  bankAccountStatus: (SimplifiedBankAccountStatus | null);
  bookingEmail: (string | null);
  externalAccessibilityData: (ExternalAccessibilityDataModelV2 | null);
  hasCreatedOffer: boolean;
  hasNonFreeOffers: boolean;
  id: number;
  isActive: boolean;
  isCaledonian: boolean;
  isPermanent: boolean;
  isValidated: boolean;
  isVirtual: boolean;
  location: (LocationResponseModelV2 | null);
  managingOffererId: number;
  mentalDisabilityCompliant: (boolean | null);
  motorDisabilityCompliant: (boolean | null);
  name: string;
  offererName: string;
  publicName: string;
  siret: (string | null);
  venueTypeCode: VenueTypeCodeKey;
  visualDisabilityCompliant: (boolean | null);
  withdrawalDetails: (string | null);
};


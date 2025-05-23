/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AddressResponseIsLinkedToVenueModel } from './AddressResponseIsLinkedToVenueModel';
import type { ExternalAccessibilityDataModel } from './ExternalAccessibilityDataModel';
import type { VenueTypeCode } from './VenueTypeCode';
export type VenueListItemResponseModel = {
  address?: AddressResponseIsLinkedToVenueModel | null;
  audioDisabilityCompliant?: boolean | null;
  bookingEmail?: string | null;
  externalAccessibilityData?: ExternalAccessibilityDataModel | null;
  hasCreatedOffer: boolean;
  id: number;
  isPermanent: boolean;
  isVirtual: boolean;
  managingOffererId: number;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  offererName: string;
  publicName?: string | null;
  siret?: string | null;
  venueTypeCode: VenueTypeCode;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDetails?: string | null;
};


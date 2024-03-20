/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { VenueTypeCode } from './VenueTypeCode';
export type VenueListItemResponseModel = {
  audioDisabilityCompliant?: boolean | null;
  bookingEmail?: string | null;
  collectiveSubCategoryId?: string | null;
  hasCreatedOffer: boolean;
  hasMissingReimbursementPoint: boolean;
  id: number;
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


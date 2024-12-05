/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AddressBodyModel } from './AddressBodyModel';
import type { VenueContactModel } from './VenueContactModel';
export type PostVenueBodyModel = {
  address: AddressBodyModel;
  audioDisabilityCompliant?: boolean | null;
  bookingEmail: string;
  comment?: string | null;
  contact?: VenueContactModel | null;
  description?: string | null;
  managingOffererId: number;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  publicName?: string | null;
  siret?: string | null;
  venueLabelId?: number | null;
  venueTypeCode: string;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDetails?: string | null;
};


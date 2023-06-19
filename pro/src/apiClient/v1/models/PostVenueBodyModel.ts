/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { VenueContactModel } from './VenueContactModel';

export type PostVenueBodyModel = {
  address: string;
  audioDisabilityCompliant?: boolean | null;
  bookingEmail: string;
  city: string;
  comment?: string | null;
  contact?: VenueContactModel | null;
  description?: string | null;
  latitude: number;
  longitude: number;
  managingOffererId: number;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  postalCode: string;
  publicName?: string | null;
  siret?: string | null;
  venueLabelId?: number | null;
  venueTypeCode: string;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDetails?: string | null;
};


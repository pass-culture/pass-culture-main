/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { DMSApplicationForEAC } from './DMSApplicationForEAC';
import type { VenueTypeCode } from './VenueTypeCode';

export type GetOffererVenueResponseModel = {
  adageInscriptionDate?: string | null;
  address?: string | null;
  audioDisabilityCompliant?: boolean | null;
  bookingEmail?: string | null;
  city?: string | null;
  collectiveDmsApplications: Array<DMSApplicationForEAC>;
  comment?: string | null;
  departementCode?: string | null;
  hasAdageId: boolean;
  hasCreatedOffer: boolean;
  hasMissingReimbursementPoint: boolean;
  id: string;
  isVirtual: boolean;
  managingOffererId: string;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  nonHumanizedId: number;
  postalCode?: string | null;
  publicName?: string | null;
  siret?: string | null;
  venueLabelId?: string | null;
  venueTypeCode: VenueTypeCode;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDetails?: string | null;
};


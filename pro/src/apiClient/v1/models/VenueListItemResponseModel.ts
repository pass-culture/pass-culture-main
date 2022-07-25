/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BusinessUnitResponseModel } from './BusinessUnitResponseModel';

export type VenueListItemResponseModel = {
  audioDisabilityCompliant?: boolean | null;
  bookingEmail?: string | null;
  businessUnit?: BusinessUnitResponseModel | null;
  businessUnitId?: number | null;
  id: string;
  isBusinessUnitMainVenue?: boolean | null;
  isVirtual: boolean;
  managingOffererId: string;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  offererName: string;
  publicName?: string | null;
  siret?: string | null;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDetails?: string | null;
};


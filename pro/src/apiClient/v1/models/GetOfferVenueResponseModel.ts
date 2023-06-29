/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { GetOfferManagingOffererResponseModel } from './GetOfferManagingOffererResponseModel';

export type GetOfferVenueResponseModel = {
  address?: string | null;
  audioDisabilityCompliant?: boolean | null;
  bookingEmail?: string | null;
  city?: string | null;
  departementCode?: string | null;
  id: number;
  isVirtual: boolean;
  managingOfferer: GetOfferManagingOffererResponseModel;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  postalCode?: string | null;
  publicName?: string | null;
  visualDisabilityCompliant?: boolean | null;
};


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
  id: string;
  isVirtual: boolean;
  managingOfferer: GetOfferManagingOffererResponseModel;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  nonHumanizedId: number;
  postalCode?: string | null;
  publicName?: string | null;
  visualDisabilityCompliant?: boolean | null;
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Coordinates } from './Coordinates';
import type { OfferManagingOffererResponse } from './OfferManagingOffererResponse';

export type OfferVenueResponse = {
  address?: string | null;
  city?: string | null;
  coordinates: Coordinates;
  id: number;
  managingOfferer: OfferManagingOffererResponse;
  name: string;
  postalCode?: string | null;
  publicName?: string | null;
};


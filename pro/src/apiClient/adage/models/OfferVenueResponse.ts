/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Coordinates } from './Coordinates';
import type { OfferManagingOffererResponse } from './OfferManagingOffererResponse';
export type OfferVenueResponse = {
  adageId?: string | null;
  address?: string | null;
  city?: string | null;
  coordinates: Coordinates;
  distance?: number | null;
  id: number;
  imgUrl?: string | null;
  managingOfferer: OfferManagingOffererResponse;
  name: string;
  postalCode?: string | null;
  publicName?: string | null;
};


/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OffererResponse } from './OffererResponse';
import type { VenueResponse } from './VenueResponse';
export type GetOffererVenuesResponse = {
  /**
   * Offerer to which the venues belong. Entity linked to the api key used.
   */
  offerer: OffererResponse;
  venues: Array<VenueResponse>;
};


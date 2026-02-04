/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveLocationType } from './CollectiveLocationType';
import type { LocationBodyModelV2 } from './LocationBodyModelV2';
import type { LocationOnlyOnVenueBodyModelV2 } from './LocationOnlyOnVenueBodyModelV2';
export type CollectiveOfferLocationModelV2 = {
  location?: (LocationBodyModelV2 | LocationOnlyOnVenueBodyModelV2 | null);
  locationComment?: (string | null);
  locationType: CollectiveLocationType;
};


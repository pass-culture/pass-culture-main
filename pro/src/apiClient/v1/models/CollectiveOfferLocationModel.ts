/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveLocationType } from './CollectiveLocationType';
import type { LocationBodyModel } from './LocationBodyModel';
import type { LocationOnlyOnVenueBodyModel } from './LocationOnlyOnVenueBodyModel';
export type CollectiveOfferLocationModel = {
  location?: (LocationBodyModel | LocationOnlyOnVenueBodyModel) | null;
  locationComment?: string | null;
  locationType: CollectiveLocationType;
};


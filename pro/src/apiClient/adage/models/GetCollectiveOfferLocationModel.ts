/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AddressResponseIsLinkedToVenueModel } from './AddressResponseIsLinkedToVenueModel';
import type { CollectiveLocationType } from './CollectiveLocationType';
export type GetCollectiveOfferLocationModel = {
  address?: AddressResponseIsLinkedToVenueModel | null;
  locationComment?: string | null;
  locationType: CollectiveLocationType;
};


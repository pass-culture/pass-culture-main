/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AddressResponseWithOAModel } from './AddressResponseWithOAModel';
import type { CollectiveLocationType } from './CollectiveLocationType';
export type GetCollectiveOfferLocationModel = {
  address?: AddressResponseWithOAModel | null;
  locationComment?: string | null;
  locationType: CollectiveLocationType;
};


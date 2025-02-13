/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AddressBodyModel } from './AddressBodyModel';
import type { CollectiveLocationType } from './CollectiveLocationType';
export type CollectiveOfferLocationModel = {
  address?: AddressBodyModel | null;
  locationComment?: string | null;
  locationType: CollectiveLocationType;
};


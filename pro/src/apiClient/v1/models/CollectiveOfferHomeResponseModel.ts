/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferAllowedAction } from './CollectiveOfferAllowedAction';
import type { CollectiveOfferDisplayedStatus } from './CollectiveOfferDisplayedStatus';
import type { CollectiveStockHomeResponseModel } from './CollectiveStockHomeResponseModel';
export type CollectiveOfferHomeResponseModel = {
  allowedActions: Array<CollectiveOfferAllowedAction>;
  collectiveStock: (CollectiveStockHomeResponseModel | null);
  displayedStatus: CollectiveOfferDisplayedStatus;
  id: number;
  imageUrl: (string | null);
  name: string;
};


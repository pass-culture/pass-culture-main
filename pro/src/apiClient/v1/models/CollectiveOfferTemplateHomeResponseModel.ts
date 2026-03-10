/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferDisplayedStatus } from './CollectiveOfferDisplayedStatus';
import type { CollectiveOfferTemplateAllowedAction } from './CollectiveOfferTemplateAllowedAction';
import type { DatesModel } from './DatesModel';
export type CollectiveOfferTemplateHomeResponseModel = {
  allowedActions: Array<CollectiveOfferTemplateAllowedAction>;
  dates: (DatesModel | null);
  displayedStatus: CollectiveOfferDisplayedStatus;
  id: number;
  imageUrl: (string | null);
  name: string;
};


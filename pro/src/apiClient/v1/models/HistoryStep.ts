/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferDisplayedStatus } from './CollectiveOfferDisplayedStatus';
import type { HistoryTransitionalStatus } from './HistoryTransitionalStatus';
export type HistoryStep = {
  datetime?: string | null;
  status: (CollectiveOfferDisplayedStatus | HistoryTransitionalStatus);
};


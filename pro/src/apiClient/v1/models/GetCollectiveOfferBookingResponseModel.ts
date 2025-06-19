/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveBookingCancellationReasons } from './CollectiveBookingCancellationReasons';
import type { CollectiveBookingStatus } from './CollectiveBookingStatus';
export type GetCollectiveOfferBookingResponseModel = {
  cancellationLimitDate: string;
  cancellationReason?: CollectiveBookingCancellationReasons | null;
  confirmationLimitDate: string;
  dateCreated: string;
  id: number;
  status: CollectiveBookingStatus;
};


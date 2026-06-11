/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveAdditionalFeeModel } from './CollectiveAdditionalFeeModel';
export type CollectiveStockCreationBodyModel = {
  additionalFees?: (Array<CollectiveAdditionalFeeModel> | null);
  bookingLimitDatetime: (string | null);
  endDatetime: string;
  numberOfTeachers?: (number | null);
  numberOfTickets: number;
  offerId: number;
  price: number;
  priceDetail?: (string | null);
  servicePrice?: (number | null);
  startDatetime: string;
};


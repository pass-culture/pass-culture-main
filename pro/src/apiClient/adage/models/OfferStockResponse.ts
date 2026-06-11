/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveAdditionalFeeResponse } from './CollectiveAdditionalFeeResponse';
export type OfferStockResponse = {
  bookingLimitDatetime?: string | null;
  collectiveAdditionalFees: Array<CollectiveAdditionalFeeResponse>;
  educationalPriceDetail?: string | null;
  endDatetime?: string | null;
  id: number;
  numberOfTeachers?: number | null;
  numberOfTickets?: number | null;
  price: number;
  servicePrice?: number | null;
  startDatetime?: string | null;
};


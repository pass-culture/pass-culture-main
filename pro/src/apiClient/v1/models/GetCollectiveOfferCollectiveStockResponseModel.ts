/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveAdditionalFeeResponseModel } from './CollectiveAdditionalFeeResponseModel';
export type GetCollectiveOfferCollectiveStockResponseModel = {
  bookingLimitDatetime: string;
  collectiveAdditionalFees: Array<CollectiveAdditionalFeeResponseModel>;
  educationalPriceDetail: (string | null);
  endDatetime: string;
  id: number;
  numberOfTeachers: number;
  numberOfTickets: number;
  price: number;
  servicePrice: (number | null);
  startDatetime: string;
};


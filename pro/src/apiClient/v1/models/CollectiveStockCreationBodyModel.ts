/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type CollectiveStockCreationBodyModel = {
  beginningDatetime: string;
  bookingLimitDatetime?: string | null;
  educationalPriceDetail?: string | null;
  numberOfTickets: number;
  offerId: number;
  totalPrice: number;
};


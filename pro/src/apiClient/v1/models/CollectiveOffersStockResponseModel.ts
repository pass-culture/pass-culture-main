/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type CollectiveOffersStockResponseModel = {
  beginningDatetime?: string | null;
  bookingLimitDatetime?: string | null;
  hasBookingLimitDatetimePassed: boolean;
  id: string;
  offerId: string;
  remainingQuantity: (number | string);
};


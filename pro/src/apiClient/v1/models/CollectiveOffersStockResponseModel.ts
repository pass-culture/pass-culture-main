/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type CollectiveOffersStockResponseModel = {
  beginningDatetime?: string | null;
  bookingLimitDatetime?: string | null;
  hasBookingLimitDatetimePassed: boolean;
  remainingQuantity: (number | string);
};


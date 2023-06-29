/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type ListOffersStockResponseModel = {
  beginningDatetime?: string | null;
  bookingQuantity?: number | null;
  hasBookingLimitDatetimePassed: boolean;
  id: number;
  remainingQuantity: (number | string);
};


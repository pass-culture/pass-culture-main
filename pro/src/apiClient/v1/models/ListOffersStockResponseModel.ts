/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type ListOffersStockResponseModel = {
  beginningDatetime?: string | null;
  hasBookingLimitDatetimePassed: boolean;
  id: string;
  nonHumanizedId: number;
  offerId: string;
  remainingQuantity: (number | string);
};


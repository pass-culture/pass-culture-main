/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type GetOfferStockResponseModel = {
  activationCodesExpirationDatetime?: string | null;
  beginningDatetime?: string | null;
  bookingLimitDatetime?: string | null;
  bookingsQuantity: number;
  dateCreated: string;
  dateModified: string;
  hasActivationCode: boolean;
  isBookable: boolean;
  isEventDeletable: boolean;
  isEventExpired: boolean;
  isSoftDeleted: boolean;
  nonHumanizedId: number;
  price: number;
  priceCategoryId?: number | null;
  quantity?: number | null;
  remainingQuantity?: (number | string) | null;
};


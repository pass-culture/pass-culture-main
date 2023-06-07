/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type GetOfferStockResponseModel = {
  activationCodesExpirationDatetime?: string | null;
  beginningDatetime?: string | null;
  bookingLimitDatetime?: string | null;
  bookingsQuantity: number;
  cancellationLimitDate?: string | null;
  dateCreated: string;
  dateModified: string;
  dateModifiedAtLastProvider?: string | null;
  fieldsUpdated: Array<string>;
  hasActivationCode: boolean;
  idAtProviders?: string | null;
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


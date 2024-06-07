/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferDisplayedStatus } from './CollectiveOfferDisplayedStatus';
import type { CollectiveOfferType } from './CollectiveOfferType';
import type { OfferStatus } from './OfferStatus';
export type ListOffersQueryModel = {
  categoryId?: string | null;
  collectiveOfferType?: CollectiveOfferType | null;
  creationMode?: string | null;
  nameOrIsbn?: string | null;
  offererId?: number | null;
  periodBeginningDate?: string | null;
  periodEndingDate?: string | null;
  status?: (OfferStatus | CollectiveOfferDisplayedStatus) | null;
  venueId?: number | null;
};


/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferDisplayedStatus } from './CollectiveOfferDisplayedStatus';
import type { CollectiveOfferType } from './CollectiveOfferType';
import type { EacFormat } from './EacFormat';
export type ListCollectiveOffersQueryModel = {
  categoryId?: string | null;
  collectiveOfferType?: CollectiveOfferType | null;
  creationMode?: string | null;
  format?: EacFormat | null;
  nameOrIsbn?: string | null;
  offererId?: number | null;
  periodBeginningDate?: string | null;
  periodEndingDate?: string | null;
  status?: (Array<CollectiveOfferDisplayedStatus> | CollectiveOfferDisplayedStatus) | null;
  venueId?: number | null;
};


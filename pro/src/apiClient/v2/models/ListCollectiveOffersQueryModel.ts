/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { OfferStatus } from './OfferStatus';

export type ListCollectiveOffersQueryModel = {
  periodBeginningDate?: string | null;
  periodEndingDate?: string | null;
  status?: OfferStatus | null;
  venueId?: number | null;
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ProviderResponse } from './ProviderResponse';

export type VenueProviderResponse = {
  dateModifiedAtLastProvider?: string;
  fieldsUpdated: Array<string>;
  id: number;
  idAtProviders?: string;
  isActive: boolean;
  isDuo?: boolean;
  isFromAllocineProvider: boolean;
  lastProviderId?: string;
  lastSyncDate?: string;
  nOffers: number;
  price?: number;
  provider: ProviderResponse;
  providerId: number;
  quantity?: number;
  venueId: number;
  venueIdAtOfferProvider: string;
};


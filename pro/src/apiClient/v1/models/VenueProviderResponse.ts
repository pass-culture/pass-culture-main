/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProviderResponse } from './ProviderResponse';
export type VenueProviderResponse = {
  id: number;
  isActive: boolean;
  isDuo?: boolean;
  isFromAllocineProvider: boolean;
  lastSyncDate?: string;
  price?: number;
  provider: ProviderResponse;
  quantity?: number;
  venueId: number;
  venueIdAtOfferProvider?: string;
};


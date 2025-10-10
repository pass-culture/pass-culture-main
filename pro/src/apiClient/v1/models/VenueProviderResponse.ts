/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProviderOfVenueResponse } from './ProviderOfVenueResponse';
export type VenueProviderResponse = {
  dateCreated: string;
  id: number;
  isActive: boolean;
  isDuo?: boolean | null;
  isFromAllocineProvider: boolean;
  lastSyncDate?: string | null;
  price?: number | null;
  provider: ProviderOfVenueResponse;
  quantity?: number | null;
  venueId: number;
  venueIdAtOfferProvider?: string | null;
};


/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ArtistOfferResponseModel } from './ArtistOfferResponseModel';
export type MinimalPostOfferBodyModel = {
  artistOfferLinks?: Array<ArtistOfferResponseModel> | null;
  audioDisabilityCompliant: boolean;
  description?: string | null;
  durationMinutes?: number | null;
  extraData?: Record<string, any> | null;
  mentalDisabilityCompliant: boolean;
  motorDisabilityCompliant: boolean;
  name: string;
  subcategoryId: string;
  venueId: number;
  visualDisabilityCompliant: boolean;
};


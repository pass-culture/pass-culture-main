/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OfferExtraData } from './OfferExtraData';
export type PostDraftOfferBodyModel = {
  description?: string | null;
  durationMinutes?: number | null;
  extraData?: OfferExtraData | null;
  name: string;
  subcategoryId: string;
  venueId: number;
};


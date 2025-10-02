/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BannerMetaModel } from './BannerMetaModel';
import type { DMSApplicationForEAC } from './DMSApplicationForEAC';
import type { VenueTypeCode } from './VenueTypeCode';
export type GetOffererVenueResponseModel = {
  bannerMeta?: BannerMetaModel | null;
  bannerUrl?: string | null;
  bookingEmail?: string | null;
  collectiveDmsApplications: Array<DMSApplicationForEAC>;
  hasAdageId: boolean;
  hasCreatedOffer: boolean;
  hasPartnerPage: boolean;
  hasVenueProviders: boolean;
  id: number;
  isPermanent: boolean;
  isVirtual: boolean;
  name: string;
  publicName?: string | null;
  siret?: string | null;
  venueTypeCode: VenueTypeCode;
  withdrawalDetails?: string | null;
};


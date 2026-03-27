/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BannerMetaModelV2 } from './BannerMetaModelV2';
import type { DisplayableActivity } from './DisplayableActivity';
import type { DMSApplicationForEACv2 } from './DMSApplicationForEACv2';
export type GetOffererVenueResponseModel = {
  activity: (DisplayableActivity | null);
  bannerMeta: (BannerMetaModelV2 | null);
  bannerUrl: (string | null);
  bookingEmail: (string | null);
  collectiveDmsApplications: Array<DMSApplicationForEACv2>;
  hasAdageId: boolean;
  hasCreatedOffer: boolean;
  hasPartnerPage: boolean;
  hasVenueProviders: boolean;
  id: number;
  isPermanent: boolean;
  isVirtual: boolean;
  name: string;
  publicName: string;
  siret: (string | null);
  withdrawalDetails: (string | null);
};


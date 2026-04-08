/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BannerMetaModel } from './BannerMetaModel';
import type { DisplayableActivity } from './DisplayableActivity';
import type { DMSApplicationForEAC } from './DMSApplicationForEAC';
export type GetOffererVenueResponseModel = {
  activity: (DisplayableActivity | null);
  bannerMeta: (BannerMetaModel | null);
  bannerUrl: (string | null);
  bookingEmail: (string | null);
  collectiveDmsApplications: Array<DMSApplicationForEAC>;
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


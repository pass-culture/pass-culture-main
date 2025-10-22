/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AddressResponseIsLinkedToVenueModel } from './AddressResponseIsLinkedToVenueModel';
import type { BannerMetaModel } from './BannerMetaModel';
import type { DMSApplicationForEAC } from './DMSApplicationForEAC';
import type { ExternalAccessibilityDataModel } from './ExternalAccessibilityDataModel';
import type { GetVenueManagingOffererResponseModel } from './GetVenueManagingOffererResponseModel';
import type { VenueTypeCode } from './VenueTypeCode';
import type { VenueTypeResponseModel } from './VenueTypeResponseModel';
export type VenueListItemResponseModel = {
  address?: AddressResponseIsLinkedToVenueModel | null;
  audioDisabilityCompliant?: boolean | null;
  bannerMeta?: BannerMetaModel | null;
  bannerUrl?: string | null;
  bookingEmail?: string | null;
  collectiveDmsApplications: Array<DMSApplicationForEAC>;
  externalAccessibilityData?: ExternalAccessibilityDataModel | null;
  hasCreatedOffer: boolean;
  hasOffers: boolean;
  hasPartnerPage: boolean;
  hasVenueProviders: boolean;
  id: number;
  isCaledonian: boolean;
  isPermanent: boolean;
  isVirtual: boolean;
  managingOfferer: GetVenueManagingOffererResponseModel;
  managingOffererId: number;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  offererName: string;
  publicName?: string | null;
  siret?: string | null;
  venueType: VenueTypeResponseModel;
  venueTypeCode: VenueTypeCode;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDetails?: string | null;
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BannerMetaModel } from './BannerMetaModel';
import type { BusinessUnitResponseModel } from './BusinessUnitResponseModel';
import type { GetVenueManagingOffererResponseModel } from './GetVenueManagingOffererResponseModel';
import type { VenueContactModel } from './VenueContactModel';
import type { VenueTypeCode } from './VenueTypeCode';

export type GetVenueResponseModel = {
  address?: string | null;
  audioDisabilityCompliant?: boolean | null;
  bannerMeta?: BannerMetaModel | null;
  bannerUrl?: string | null;
  bic?: string | null;
  bookingEmail?: string | null;
  businessUnit?: BusinessUnitResponseModel | null;
  businessUnitId?: number | null;
  city?: string | null;
  comment?: string | null;
  contact?: VenueContactModel | null;
  dateCreated: string;
  dateModifiedAtLastProvider?: string | null;
  demarchesSimplifieesApplicationId?: string | null;
  departementCode?: string | null;
  description?: string | null;
  fieldsUpdated: Array<string>;
  iban?: string | null;
  id: string;
  idAtProviders?: string | null;
  isBusinessUnitMainVenue?: boolean | null;
  isPermanent?: boolean | null;
  isValidated: boolean;
  isVirtual: boolean;
  lastProviderId?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  managingOfferer: GetVenueManagingOffererResponseModel;
  managingOffererId: string;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  nonHumanizedId: number;
  postalCode?: string | null;
  pricingPointId?: number | null;
  publicName?: string | null;
  reimbursementPointId?: number | null;
  siret?: string | null;
  venueLabelId?: string | null;
  venueTypeCode?: VenueTypeCode | null;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDetails?: string | null;
};


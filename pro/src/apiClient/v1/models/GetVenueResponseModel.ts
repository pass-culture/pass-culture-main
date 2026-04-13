/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BannerMetaModel } from './BannerMetaModel';
import type { DisplayableActivity } from './DisplayableActivity';
import type { DMSApplicationForEAC } from './DMSApplicationForEAC';
import type { ExternalAccessibilityDataModelV2 } from './ExternalAccessibilityDataModelV2';
import type { GetVenueDomainResponseModel } from './GetVenueDomainResponseModel';
import type { GetVenueManagingOffererResponseModel } from './GetVenueManagingOffererResponseModel';
import type { GetVenuePricingPointResponseModel } from './GetVenuePricingPointResponseModel';
import type { LegalStatusResponseModel } from './LegalStatusResponseModel';
import type { LocationResponseModelV2 } from './LocationResponseModelV2';
import type { SimplifiedBankAccountStatus } from './SimplifiedBankAccountStatus';
import type { StudentLevels } from './StudentLevels';
import type { VenueContactModelV2 } from './VenueContactModelV2';
import type { WeekdayOpeningHoursTimespansV2 } from './WeekdayOpeningHoursTimespansV2';
export type GetVenueResponseModel = {
  activity?: (DisplayableActivity | null);
  adageInscriptionDate?: (string | null);
  allowedOnAdage: boolean;
  audioDisabilityCompliant?: (boolean | null);
  bankAccountStatus?: (SimplifiedBankAccountStatus | null);
  bannerMeta?: (BannerMetaModel | null);
  bannerUrl?: (string | null);
  bookingEmail?: (string | null);
  canDisplayHighlights: boolean;
  collectiveDescription?: (string | null);
  collectiveDomains: Array<GetVenueDomainResponseModel>;
  collectiveEmail?: (string | null);
  collectiveInterventionArea?: (Array<string> | null);
  collectiveLegalStatus?: (LegalStatusResponseModel | null);
  collectivePhone?: (string | null);
  collectiveStudents?: (Array<StudentLevels> | null);
  collectiveWebsite?: (string | null);
  comment?: (string | null);
  contact?: (VenueContactModelV2 | null);
  dateCreated: string;
  description: (string | null);
  externalAccessibilityData?: (ExternalAccessibilityDataModelV2 | null);
  externalAccessibilityId?: (string | null);
  hasActiveIndividualOffer: boolean;
  hasAdageId: boolean;
  hasNonDraftOffers: boolean;
  hasNonFreeOffers: boolean;
  hasOffers: boolean;
  hasPartnerPage: boolean;
  id: number;
  isCaledonian: boolean;
  isOpenToPublic: boolean;
  isPermanent?: (boolean | null);
  isValidated: boolean;
  isVirtual: boolean;
  lastCollectiveDmsApplication: (DMSApplicationForEAC | null);
  location: LocationResponseModelV2;
  managingOfferer: GetVenueManagingOffererResponseModel;
  mentalDisabilityCompliant?: (boolean | null);
  motorDisabilityCompliant?: (boolean | null);
  name: string;
  openingHours?: (WeekdayOpeningHoursTimespansV2 | null);
  pricingPoint?: (GetVenuePricingPointResponseModel | null);
  publicName: string;
  siret?: (string | null);
  visualDisabilityCompliant?: (boolean | null);
  volunteeringUrl: (string | null);
  withdrawalDetails?: (string | null);
};


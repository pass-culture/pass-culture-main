/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BankAccountResponseModel } from './BankAccountResponseModel';
import type { BannerMetaModel } from './BannerMetaModel';
import type { DMSApplicationForEAC } from './DMSApplicationForEAC';
import type { ExternalAccessibilityDataModel } from './ExternalAccessibilityDataModel';
import type { GetVenueDomainResponseModel } from './GetVenueDomainResponseModel';
import type { GetVenueManagingOffererResponseModel } from './GetVenueManagingOffererResponseModel';
import type { GetVenuePricingPointResponseModel } from './GetVenuePricingPointResponseModel';
import type { LegalStatusResponseModel } from './LegalStatusResponseModel';
import type { StudentLevels } from './StudentLevels';
import type { VenueContactModel } from './VenueContactModel';
import type { VenueTypeCode } from './VenueTypeCode';
export type GetVenueResponseModel = {
  adageInscriptionDate?: string | null;
  address?: string | null;
  audioDisabilityCompliant?: boolean | null;
  banId?: string | null;
  bankAccount?: BankAccountResponseModel | null;
  bannerMeta?: BannerMetaModel | null;
  bannerUrl?: string | null;
  bookingEmail?: string | null;
  city?: string | null;
  collectiveAccessInformation?: string | null;
  collectiveDescription?: string | null;
  collectiveDmsApplications: Array<DMSApplicationForEAC>;
  collectiveDomains: Array<GetVenueDomainResponseModel>;
  collectiveEmail?: string | null;
  collectiveInterventionArea?: Array<string> | null;
  collectiveLegalStatus?: LegalStatusResponseModel | null;
  collectiveNetwork?: Array<string> | null;
  collectivePhone?: string | null;
  collectiveStudents?: Array<StudentLevels> | null;
  collectiveSubCategoryId?: string | null;
  collectiveWebsite?: string | null;
  comment?: string | null;
  contact?: VenueContactModel | null;
  dateCreated: string;
  demarchesSimplifieesApplicationId?: string | null;
  departementCode?: string | null;
  description?: string | null;
  dmsToken: string;
  externalAccessibilityData?: ExternalAccessibilityDataModel | null;
  hasAdageId: boolean;
  id: number;
  isPermanent?: boolean | null;
  isVirtual: boolean;
  isVisibleInApp?: boolean;
  latitude?: number | null;
  longitude?: number | null;
  managingOfferer: GetVenueManagingOffererResponseModel;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  openingHours?: Record<string, any> | null;
  postalCode?: string | null;
  pricingPoint?: GetVenuePricingPointResponseModel | null;
  publicName?: string | null;
  reimbursementPointId?: number | null;
  siret?: string | null;
  timezone: string;
  venueLabelId?: number | null;
  venueTypeCode: VenueTypeCode;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDetails?: string | null;
};


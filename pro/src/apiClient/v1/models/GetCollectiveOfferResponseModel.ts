/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveBookingStatus } from './CollectiveBookingStatus';
import type { CollectiveOfferOfferVenueResponseModel } from './CollectiveOfferOfferVenueResponseModel';
import type { CollectiveOfferStatus } from './CollectiveOfferStatus';
import type { EacFormat } from './EacFormat';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';
import type { EducationalRedactorResponseModel } from './EducationalRedactorResponseModel';
import type { GetCollectiveOfferCollectiveStockResponseModel } from './GetCollectiveOfferCollectiveStockResponseModel';
import type { GetCollectiveOfferProviderResponseModel } from './GetCollectiveOfferProviderResponseModel';
import type { GetCollectiveOfferVenueResponseModel } from './GetCollectiveOfferVenueResponseModel';
import type { NationalProgramModel } from './NationalProgramModel';
import type { OfferDomain } from './OfferDomain';
import type { StudentLevels } from './StudentLevels';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';
import type { TemplateDatesModel } from './TemplateDatesModel';
export type GetCollectiveOfferResponseModel = {
  audioDisabilityCompliant?: boolean | null;
  bookingEmails: Array<string>;
  collectiveStock?: GetCollectiveOfferCollectiveStockResponseModel | null;
  contactEmail?: string | null;
  contactPhone?: string | null;
  dateCreated: string;
  dates?: TemplateDatesModel | null;
  description: string;
  domains: Array<OfferDomain>;
  durationMinutes?: number | null;
  formats?: Array<EacFormat> | null;
  hasBookingLimitDatetimesPassed: boolean;
  id: number;
  imageCredit?: string | null;
  imageUrl?: string | null;
  institution?: EducationalInstitutionResponseModel | null;
  interventionArea: Array<string>;
  isActive: boolean;
  isBookable: boolean;
  isCancellable: boolean;
  isEditable: boolean;
  isNonFreeOffer?: boolean | null;
  isPublicApi: boolean;
  isTemplate?: boolean;
  isVisibilityEditable: boolean;
  lastBookingId?: number | null;
  lastBookingStatus?: CollectiveBookingStatus | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  nationalProgram?: NationalProgramModel | null;
  offerId?: number | null;
  offerVenue: CollectiveOfferOfferVenueResponseModel;
  provider?: GetCollectiveOfferProviderResponseModel | null;
  status: CollectiveOfferStatus;
  students: Array<StudentLevels>;
  subcategoryId?: (SubcategoryIdEnum | string) | null;
  teacher?: EducationalRedactorResponseModel | null;
  templateId?: number | null;
  venue: GetCollectiveOfferVenueResponseModel;
  visualDisabilityCompliant?: boolean | null;
};


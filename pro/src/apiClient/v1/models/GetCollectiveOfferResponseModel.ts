/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferAllowedAction } from './CollectiveOfferAllowedAction';
import type { CollectiveOfferDatesModel } from './CollectiveOfferDatesModel';
import type { CollectiveOfferDisplayedStatus } from './CollectiveOfferDisplayedStatus';
import type { CollectiveOfferHistory } from './CollectiveOfferHistory';
import type { EacFormat } from './EacFormat';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';
import type { EducationalRedactorResponseModel } from './EducationalRedactorResponseModel';
import type { GetCollectiveOfferBookingResponseModel } from './GetCollectiveOfferBookingResponseModel';
import type { GetCollectiveOfferCollectiveStockResponseModel } from './GetCollectiveOfferCollectiveStockResponseModel';
import type { GetCollectiveOfferLocationModel } from './GetCollectiveOfferLocationModel';
import type { GetCollectiveOfferProviderResponseModel } from './GetCollectiveOfferProviderResponseModel';
import type { GetCollectiveOfferVenueResponseModel } from './GetCollectiveOfferVenueResponseModel';
import type { NationalProgramModel } from './NationalProgramModel';
import type { OfferDomain } from './OfferDomain';
import type { StudentLevels } from './StudentLevels';
export type GetCollectiveOfferResponseModel = {
  allowedActions: Array<CollectiveOfferAllowedAction>;
  audioDisabilityCompliant?: boolean | null;
  booking?: GetCollectiveOfferBookingResponseModel | null;
  bookingEmails: Array<string>;
  collectiveStock?: GetCollectiveOfferCollectiveStockResponseModel | null;
  contactEmail?: string | null;
  contactPhone?: string | null;
  dateCreated: string;
  dates?: CollectiveOfferDatesModel | null;
  description: string;
  displayedStatus: CollectiveOfferDisplayedStatus;
  domains: Array<OfferDomain>;
  durationMinutes?: number | null;
  formats: Array<EacFormat>;
  history: CollectiveOfferHistory;
  id: number;
  imageCredit?: string | null;
  imageUrl?: string | null;
  institution?: EducationalInstitutionResponseModel | null;
  interventionArea: Array<string>;
  isPublicApi: boolean;
  isTemplate?: boolean;
  location: GetCollectiveOfferLocationModel;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  nationalProgram?: NationalProgramModel | null;
  provider?: GetCollectiveOfferProviderResponseModel | null;
  students: Array<StudentLevels>;
  teacher?: EducationalRedactorResponseModel | null;
  templateId?: number | null;
  venue: GetCollectiveOfferVenueResponseModel;
  visualDisabilityCompliant?: boolean | null;
};


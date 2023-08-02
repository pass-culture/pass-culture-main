/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveBookingStatus } from './CollectiveBookingStatus';
import type { CollectiveOfferOfferVenueResponseModel } from './CollectiveOfferOfferVenueResponseModel';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';
import type { EducationalRedactorResponseModel } from './EducationalRedactorResponseModel';
import type { GetCollectiveOfferCollectiveStockResponseModel } from './GetCollectiveOfferCollectiveStockResponseModel';
import type { GetCollectiveOfferVenueResponseModel } from './GetCollectiveOfferVenueResponseModel';
import type { OfferDomain } from './OfferDomain';
import type { OfferStatus } from './OfferStatus';
import type { StudentLevels } from './StudentLevels';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';

export type GetCollectiveOfferResponseModel = {
  audioDisabilityCompliant?: boolean | null;
  bookingEmails: Array<string>;
  collectiveStock?: GetCollectiveOfferCollectiveStockResponseModel | null;
  contactEmail: string;
  contactPhone?: string | null;
  dateCreated: string;
  description: string;
  domains: Array<OfferDomain>;
  durationMinutes?: number | null;
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
  isPublicApi: boolean;
  isVisibilityEditable: boolean;
  lastBookingId?: number | null;
  lastBookingStatus?: CollectiveBookingStatus | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  nationalProgramId?: number | null;
  offerId?: number | null;
  offerVenue: CollectiveOfferOfferVenueResponseModel;
  status: OfferStatus;
  students: Array<StudentLevels>;
  subcategoryId: SubcategoryIdEnum;
  teacher?: EducationalRedactorResponseModel | null;
  templateId?: number | null;
  venue: GetCollectiveOfferVenueResponseModel;
  visualDisabilityCompliant?: boolean | null;
};


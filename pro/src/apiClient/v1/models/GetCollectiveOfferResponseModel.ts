/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveOfferOfferVenueResponseModel } from './CollectiveOfferOfferVenueResponseModel';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';
import type { GetCollectiveOfferCollectiveStockResponseModel } from './GetCollectiveOfferCollectiveStockResponseModel';
import type { GetCollectiveOfferVenueResponseModel } from './GetCollectiveOfferVenueResponseModel';
import type { OfferDomain } from './OfferDomain';
import type { OfferStatus } from './OfferStatus';
import type { StudentLevels } from './StudentLevels';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';

export type GetCollectiveOfferResponseModel = {
  audioDisabilityCompliant?: boolean | null;
  bookingEmail?: string | null;
  collectiveStock?: GetCollectiveOfferCollectiveStockResponseModel | null;
  contactEmail: string;
  contactPhone: string;
  dateCreated: string;
  description?: string | null;
  domains: Array<OfferDomain>;
  durationMinutes?: number | null;
  hasBookingLimitDatetimesPassed: boolean;
  id: string;
  institution?: EducationalInstitutionResponseModel | null;
  interventionArea: Array<string>;
  isActive: boolean;
  isBookable: boolean;
  isEditable: boolean;
  isVisibilityEditable: boolean;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  nonHumanizedId: number;
  offerId?: string | null;
  offerVenue: CollectiveOfferOfferVenueResponseModel;
  status: OfferStatus;
  students: Array<StudentLevels>;
  subcategoryId: SubcategoryIdEnum;
  venue: GetCollectiveOfferVenueResponseModel;
  venueId: string;
  visualDisabilityCompliant?: boolean | null;
};


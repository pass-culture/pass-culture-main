/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveOfferOfferVenue } from './CollectiveOfferOfferVenue';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';
import type { EducationalRedactorResponseModel } from './EducationalRedactorResponseModel';
import type { OfferDomain } from './OfferDomain';
import type { OfferStockResponse } from './OfferStockResponse';
import type { OfferVenueResponse } from './OfferVenueResponse';
import type { StudentLevels } from './StudentLevels';

export type CollectiveOfferResponseModel = {
  audioDisabilityCompliant: boolean;
  contactEmail: string;
  contactPhone?: string | null;
  description?: string | null;
  domains: Array<OfferDomain>;
  durationMinutes?: number | null;
  educationalInstitution?: EducationalInstitutionResponseModel | null;
  educationalPriceDetail?: string | null;
  id: number;
  imageCredit?: string | null;
  imageUrl?: string | null;
  interventionArea: Array<string>;
  isExpired: boolean;
  isSoldOut: boolean;
  mentalDisabilityCompliant: boolean;
  motorDisabilityCompliant: boolean;
  name: string;
  nationalProgramId?: number | null;
  offerId?: string | null;
  offerVenue: CollectiveOfferOfferVenue;
  stock: OfferStockResponse;
  students: Array<StudentLevels>;
  subcategoryLabel: string;
  teacher?: EducationalRedactorResponseModel | null;
  venue: OfferVenueResponse;
  visualDisabilityCompliant: boolean;
};


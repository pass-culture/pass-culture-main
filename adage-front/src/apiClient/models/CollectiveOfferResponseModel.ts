/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveOfferOfferVenue } from './CollectiveOfferOfferVenue';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';
import type { OfferDomain } from './OfferDomain';
import type { OfferStockResponse } from './OfferStockResponse';
import type { OfferVenueResponse } from './OfferVenueResponse';
import type { StudentLevels } from './StudentLevels';

export type CollectiveOfferResponseModel = {
  audioDisabilityCompliant: boolean;
  contactEmail: string;
  contactPhone: string;
  description?: string | null;
  domains: Array<OfferDomain>;
  durationMinutes?: number | null;
  educationalInstitution?: EducationalInstitutionResponseModel | null;
  educationalPriceDetail?: string | null;
  id: number;
  interventionArea: Array<string>;
  isExpired: boolean;
  isSoldOut: boolean;
  mentalDisabilityCompliant: boolean;
  motorDisabilityCompliant: boolean;
  name: string;
  offerId?: string | null;
  offerVenue: CollectiveOfferOfferVenue;
  stock: OfferStockResponse;
  students: Array<StudentLevels>;
  subcategoryLabel: string;
  venue: OfferVenueResponse;
  visualDisabilityCompliant: boolean;
};


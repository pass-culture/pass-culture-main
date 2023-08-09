/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveOfferOfferVenue } from './CollectiveOfferOfferVenue';
import type { NationalProgramModel } from './NationalProgramModel';
import type { OfferDomain } from './OfferDomain';
import type { OfferVenueResponse } from './OfferVenueResponse';
import type { StudentLevels } from './StudentLevels';

export type CollectiveOfferTemplateResponseModel = {
  audioDisabilityCompliant: boolean;
  contactEmail: string;
  contactPhone?: string | null;
  description?: string | null;
  domains: Array<OfferDomain>;
  durationMinutes?: number | null;
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
  nationalProgram?: NationalProgramModel | null;
  offerId?: string | null;
  offerVenue: CollectiveOfferOfferVenue;
  students: Array<StudentLevels>;
  subcategoryLabel: string;
  venue: OfferVenueResponse;
  visualDisabilityCompliant: boolean;
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EducationalOfferExtraDataOfferVenueBodyModel } from './EducationalOfferExtraDataOfferVenueBodyModel';

export type EducationalOfferPartialExtraDataBodyModel = {
  contactEmail?: string | null;
  contactPhone?: string | null;
  offerVenue?: EducationalOfferExtraDataOfferVenueBodyModel | null;
  students?: Array<string> | null;
};


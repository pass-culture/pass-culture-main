/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EducationalOfferExtraDataOfferVenueBodyModel } from './EducationalOfferExtraDataOfferVenueBodyModel';
import type { StudentLevels } from './StudentLevels';

export type PostEducationalOfferExtraDataBodyModel = {
  contactEmail: string;
  contactPhone: string;
  offerVenue: EducationalOfferExtraDataOfferVenueBodyModel;
  students: Array<StudentLevels>;
};


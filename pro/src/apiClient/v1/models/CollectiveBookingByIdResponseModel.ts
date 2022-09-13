/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveBookingEducationalRedactorResponseModel } from './CollectiveBookingEducationalRedactorResponseModel';
import type { CollectiveOfferOfferVenueResponseModel } from './CollectiveOfferOfferVenueResponseModel';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';
import type { StudentLevels } from './StudentLevels';

export type CollectiveBookingByIdResponseModel = {
  beginningDatetime: string;
  educationalInstitution: EducationalInstitutionResponseModel;
  educationalRedactor: CollectiveBookingEducationalRedactorResponseModel;
  id: number;
  offerVenue: CollectiveOfferOfferVenueResponseModel;
  price: number;
  students: Array<StudentLevels>;
};


/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveBookingBankInformationStatus } from './CollectiveBookingBankInformationStatus';
import type { CollectiveBookingEducationalRedactorResponseModel } from './CollectiveBookingEducationalRedactorResponseModel';
import type { CollectiveOfferOfferVenueResponseModel } from './CollectiveOfferOfferVenueResponseModel';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';
import type { StudentLevels } from './StudentLevels';

export type CollectiveBookingByIdResponseModel = {
  bankInformationStatus: CollectiveBookingBankInformationStatus;
  beginningDatetime: string;
  educationalInstitution: EducationalInstitutionResponseModel;
  educationalRedactor: CollectiveBookingEducationalRedactorResponseModel;
  id: number;
  isCancellable: boolean;
  numberOfTickets: number;
  offerVenue: CollectiveOfferOfferVenueResponseModel;
  offererId: string;
  price: number;
  students: Array<StudentLevels>;
  venueDMSApplicationId?: number | null;
  venueId: string;
  venuePostalCode?: string | null;
};


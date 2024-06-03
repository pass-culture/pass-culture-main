/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveBookingBankAccountStatus } from './CollectiveBookingBankAccountStatus';
import type { CollectiveBookingEducationalRedactorResponseModel } from './CollectiveBookingEducationalRedactorResponseModel';
import type { CollectiveOfferOfferVenueResponseModel } from './CollectiveOfferOfferVenueResponseModel';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';
import type { StudentLevels } from './StudentLevels';
export type CollectiveBookingByIdResponseModel = {
  bankAccountStatus: CollectiveBookingBankAccountStatus;
  beginningDatetime: string;
  educationalInstitution: EducationalInstitutionResponseModel;
  educationalRedactor: CollectiveBookingEducationalRedactorResponseModel;
  endDatetime: string;
  id: number;
  isCancellable: boolean;
  numberOfTickets: number;
  offerVenue: CollectiveOfferOfferVenueResponseModel;
  offererId: number;
  price: number;
  startDatetime: string;
  students: Array<StudentLevels>;
  venueDMSApplicationId?: number | null;
  venueId: number;
  venuePostalCode?: string | null;
};


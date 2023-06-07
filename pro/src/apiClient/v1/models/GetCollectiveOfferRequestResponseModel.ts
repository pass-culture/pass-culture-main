/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveOfferInstitutionModel } from './CollectiveOfferInstitutionModel';
import type { CollectiveOfferRedactorModel } from './CollectiveOfferRedactorModel';

export type GetCollectiveOfferRequestResponseModel = {
  comment: string;
  dateCreated?: string | null;
  institution: CollectiveOfferInstitutionModel;
  phoneNumber?: string | null;
  redactor: CollectiveOfferRedactorModel;
  requestedDate?: string | null;
  totalStudents?: number | null;
  totalTeachers?: number | null;
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveOfferRedactorModel } from './CollectiveOfferRedactorModel';

export type GetCollectiveOfferRequestResponseModel = {
  comment: string;
  dateCreated?: string | null;
  institutionId: string;
  phoneNumber?: string | null;
  redactor: CollectiveOfferRedactorModel;
  requestedDate?: string | null;
  totalStudents?: number | null;
  totalTeachers?: number | null;
};


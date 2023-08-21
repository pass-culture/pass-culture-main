/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveBookingStatus } from './CollectiveBookingStatus';
import type { EducationalYearModel } from './EducationalYearModel';

export type CollectiveBookingResponseModel = {
  cancellationLimitDate?: string | null;
  confirmationDate?: string | null;
  dateCreated: string;
  dateUsed?: string | null;
  educationalYear: EducationalYearModel;
  id: number;
  status: CollectiveBookingStatus;
  venueId: number;
};


/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveBookingStatus } from './CollectiveBookingStatus';

export type CollectiveBookingResponseModel = {
  cancellationLimitDate?: string | null;
  confirmationDate?: string | null;
  dateCreated: string;
  dateUsed?: string | null;
  id: number;
  reimbursementDate?: string | null;
  status: CollectiveBookingStatus;
};


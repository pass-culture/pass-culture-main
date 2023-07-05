/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { DMSApplicationstatus } from './DMSApplicationstatus';

export type DMSApplicationForEAC = {
  application: number;
  buildDate?: string | null;
  depositDate: string;
  expirationDate?: string | null;
  instructionDate?: string | null;
  lastChangeDate: string;
  procedure: number;
  processingDate?: string | null;
  state: DMSApplicationstatus;
  userDeletionDate?: string | null;
  venueId: number;
};


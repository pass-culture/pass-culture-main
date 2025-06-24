/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveBookingCancellationReasons } from './CollectiveBookingCancellationReasons';
import type { CollectiveBookingStatus } from './CollectiveBookingStatus';
import type { EducationalRedactorResponseModel } from './EducationalRedactorResponseModel';
export type GetCollectiveOfferBookingResponseModel = {
  cancellationLimitDate: string;
  cancellationReason?: CollectiveBookingCancellationReasons | null;
  confirmationLimitDate: string;
  dateCreated: string;
  educationalRedactor?: EducationalRedactorResponseModel | null;
  id: number;
  status: CollectiveBookingStatus;
};


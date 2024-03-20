/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BookingStatusHistoryResponseModel } from './BookingStatusHistoryResponseModel';
import type { CollectiveBookingCancellationReasons } from './CollectiveBookingCancellationReasons';
import type { CollectiveBookingCollectiveStockResponseModel } from './CollectiveBookingCollectiveStockResponseModel';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';
export type CollectiveBookingResponseModel = {
  bookingAmount: number;
  bookingCancellationLimitDate: string;
  bookingCancellationReason?: CollectiveBookingCancellationReasons | null;
  bookingConfirmationDate?: string | null;
  bookingConfirmationLimitDate: string;
  bookingDate: string;
  bookingId: string;
  bookingIsDuo?: boolean;
  bookingStatus: string;
  bookingStatusHistory: Array<BookingStatusHistoryResponseModel>;
  bookingToken?: string | null;
  institution: EducationalInstitutionResponseModel;
  stock: CollectiveBookingCollectiveStockResponseModel;
};


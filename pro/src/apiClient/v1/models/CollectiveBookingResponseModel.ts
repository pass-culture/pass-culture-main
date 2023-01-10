/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BookingStatusHistoryResponseModel } from './BookingStatusHistoryResponseModel';
import type { CollectiveBookingCollectiveStockResponseModel } from './CollectiveBookingCollectiveStockResponseModel';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';

export type CollectiveBookingResponseModel = {
  bookingAmount: number;
  bookingCancellationLimitDate: string;
  bookingConfirmationDate?: string | null;
  bookingConfirmationLimitDate: string;
  bookingDate: string;
  bookingId: string;
  bookingIdentifier: string;
  bookingIsDuo?: boolean;
  bookingStatus: string;
  bookingStatusHistory: Array<BookingStatusHistoryResponseModel>;
  bookingToken?: string | null;
  institution: EducationalInstitutionResponseModel;
  stock: CollectiveBookingCollectiveStockResponseModel;
};


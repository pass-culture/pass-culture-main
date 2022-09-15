/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BookingStatusHistoryResponseModel } from './BookingStatusHistoryResponseModel';
import type { CollectiveBookingCollectiveStockResponseModel } from './CollectiveBookingCollectiveStockResponseModel';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';

export type CollectiveBookingResponseModel = {
  booking_amount: number;
  booking_date: string;
  booking_identifier: string;
  booking_is_duo?: boolean;
  booking_status: string;
  booking_status_history: Array<BookingStatusHistoryResponseModel>;
  booking_token?: string | null;
  institution: EducationalInstitutionResponseModel;
  stock: CollectiveBookingCollectiveStockResponseModel;
};


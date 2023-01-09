/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BookingRecapResponseBeneficiaryModel } from './BookingRecapResponseBeneficiaryModel';
import type { BookingRecapResponseBookingStatusHistoryModel } from './BookingRecapResponseBookingStatusHistoryModel';
import type { BookingRecapResponseStockModel } from './BookingRecapResponseStockModel';
import type { BookingRecapStatus } from './BookingRecapStatus';

export type BookingRecapResponseModel = {
  beneficiary: BookingRecapResponseBeneficiaryModel;
  booking_amount: number;
  booking_date: string;
  booking_is_duo: boolean;
  booking_status: BookingRecapStatus;
  booking_status_history: Array<BookingRecapResponseBookingStatusHistoryModel>;
  booking_token?: string | null;
  stock: BookingRecapResponseStockModel;
};


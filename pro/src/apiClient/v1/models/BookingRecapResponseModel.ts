/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BookingRecapResponseBeneficiaryModel } from './BookingRecapResponseBeneficiaryModel';
import type { BookingRecapResponseBookingStatusHistoryModel } from './BookingRecapResponseBookingStatusHistoryModel';
import type { BookingRecapResponseStockModel } from './BookingRecapResponseStockModel';
import type { BookingRecapStatus } from './BookingRecapStatus';
export type BookingRecapResponseModel = {
  beneficiary: BookingRecapResponseBeneficiaryModel;
  bookingAmount: number;
  bookingDate: string;
  bookingIsDuo: boolean;
  bookingPriceCategoryLabel?: (string | null);
  bookingStatus: BookingRecapStatus;
  bookingStatusHistory: Array<BookingRecapResponseBookingStatusHistoryModel>;
  bookingToken?: (string | null);
  stock: BookingRecapResponseStockModel;
};


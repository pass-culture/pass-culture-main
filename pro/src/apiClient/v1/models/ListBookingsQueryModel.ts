/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BookingExportType } from './BookingExportType';
import type { BookingRecapStatus } from './BookingRecapStatus';
import type { BookingStatusFilter } from './BookingStatusFilter';
export type ListBookingsQueryModel = {
  beneficiaryNameOrEmail?: (string | null);
  bookingPeriodBeginningDate?: (string | null);
  bookingPeriodEndingDate?: (string | null);
  bookingStatus?: (Array<BookingRecapStatus> | null);
  bookingStatusFilter?: (BookingStatusFilter | null);
  bookingToken?: (string | null);
  eventDate?: (string | null);
  exportType?: (BookingExportType | null);
  offerEan?: (string | null);
  offerId?: (number | null);
  offerName?: (string | null);
  offererAddressId?: (number | null);
  offererId?: (number | null);
  page?: number;
  venueId?: (number | null);
};


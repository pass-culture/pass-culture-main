/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BookingExportType } from './BookingExportType';
import type { BookingStatusFilter } from './BookingStatusFilter';
export type ListBookingsQueryModel = {
  bookingPeriodBeginningDate?: string | null;
  bookingPeriodEndingDate?: string | null;
  bookingStatusFilter?: BookingStatusFilter | null;
  eventDate?: string | null;
  exportType?: BookingExportType | null;
  offerId?: number | null;
  offererAddressId?: number | null;
  page?: number;
  venueId?: number | null;
};


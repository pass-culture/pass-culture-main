/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BookingEventType } from './BookingEventType';
import type { BookingExportType } from './BookingExportType';
import type { BookingRecapStatus } from './BookingRecapStatus';
import type { BookingSortableColumn } from './BookingSortableColumn';
import type { SortOrder } from './SortOrder';
export type ListBookingsQueryModel = {
  beneficiaryNameOrEmail?: (string | null);
  bookingPeriodBeginningDate?: (string | null);
  bookingPeriodEndingDate?: (string | null);
  bookingStatus?: (Array<BookingRecapStatus> | null);
  bookingToken?: (string | null);
  eventDate?: (string | null);
  eventType?: (BookingEventType | null);
  exportType?: (BookingExportType | null);
  offerEan?: (string | null);
  offerId?: (number | null);
  offerName?: (string | null);
  offererAddressId?: (number | null);
  offererId?: (number | null);
  page?: number;
  sortBy?: (BookingSortableColumn | null);
  sortOrder?: (SortOrder | null);
  venueId?: (number | null);
};


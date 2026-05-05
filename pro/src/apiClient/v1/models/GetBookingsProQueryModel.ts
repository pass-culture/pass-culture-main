/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BookingStatusFilter } from './BookingStatusFilter';
export type GetBookingsProQueryModel = {
  bookingPeriodBeginningDate?: (string | null);
  bookingPeriodEndingDate?: (string | null);
  bookingStatusFilter?: (BookingStatusFilter | null);
  eventDate?: (string | null);
  offerId?: (number | null);
  offererAddressId?: (number | null);
  page?: number;
  venueId: number;
};


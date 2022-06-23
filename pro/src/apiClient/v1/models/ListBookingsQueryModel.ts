/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BookingExportType } from './BookingExportType';
import type { BookingStatusFilter } from './BookingStatusFilter';
import type { OfferType } from './OfferType';

export type ListBookingsQueryModel = {
  bookingPeriodBeginningDate?: string | null;
  bookingPeriodEndingDate?: string | null;
  bookingStatusFilter?: BookingStatusFilter | null;
  eventDate?: string | null;
  exportType?: BookingExportType | null;
  extra?: string;
  offerType?: OfferType | null;
  page?: number;
  venueId?: number | null;
};


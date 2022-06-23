/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveBookingStatusFilter } from './CollectiveBookingStatusFilter';

export type ListCollectiveBookingsQueryModel = {
  bookingPeriodBeginningDate?: string | null;
  bookingPeriodEndingDate?: string | null;
  bookingStatusFilter?: CollectiveBookingStatusFilter | null;
  eventDate?: string | null;
  extra?: string;
  page?: number;
  venueId?: number | null;
};


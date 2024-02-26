/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveBookingStatusFilter } from './CollectiveBookingStatusFilter';
export type ListCollectiveBookingsQueryModel = {
  bookingPeriodBeginningDate?: string | null;
  bookingPeriodEndingDate?: string | null;
  bookingStatusFilter?: CollectiveBookingStatusFilter | null;
  eventDate?: string | null;
  page?: number;
  venueId?: number | null;
};


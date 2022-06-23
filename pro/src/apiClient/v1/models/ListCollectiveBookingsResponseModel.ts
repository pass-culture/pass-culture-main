/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveBookingResponseModel } from './CollectiveBookingResponseModel';

export type ListCollectiveBookingsResponseModel = {
  bookingsRecap: Array<CollectiveBookingResponseModel>;
  page: number;
  pages: number;
  total: number;
};


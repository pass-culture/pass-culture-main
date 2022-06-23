/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BookingRecapResponseModel } from './BookingRecapResponseModel';

export type ListBookingsResponseModel = {
  bookingsRecap: Array<BookingRecapResponseModel>;
  page: number;
  pages: number;
  total: number;
};


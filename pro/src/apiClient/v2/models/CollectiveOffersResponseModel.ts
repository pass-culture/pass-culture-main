/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveBookingResponseModel } from './CollectiveBookingResponseModel';
export type CollectiveOffersResponseModel = {
  beginningDatetime: string;
  bookings: Array<CollectiveBookingResponseModel>;
  id: number;
  status: string;
  venueId: number;
};


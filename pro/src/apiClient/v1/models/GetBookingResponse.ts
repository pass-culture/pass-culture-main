/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BookingOfferType } from './BookingOfferType';
export type GetBookingResponse = {
  bookingId: string;
  dateOfBirth: (string | null);
  datetime: string;
  ean13: (string | null);
  email: string;
  firstName: (string | null);
  isUsed: boolean;
  lastName: (string | null);
  offerAddress: (string | null);
  offerDepartmentCode: (string | null);
  offerId: number;
  offerName: string;
  offerType: BookingOfferType;
  phoneNumber: (string | null);
  price: number;
  priceCategoryLabel: (string | null);
  publicOfferId: string;
  quantity: number;
  userName: string;
  venueName: string;
};


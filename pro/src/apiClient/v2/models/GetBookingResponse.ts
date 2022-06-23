/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BookingFormula } from './BookingFormula';
import type { BookingOfferType } from './BookingOfferType';

export type GetBookingResponse = {
  bookingId: string;
  dateOfBirth: string;
  datetime: string;
  ean13?: string | null;
  email: string;
  formula?: BookingFormula | null;
  isUsed: boolean;
  offerId: number;
  offerName: string;
  offerType: BookingOfferType;
  phoneNumber: string;
  price: number;
  publicOfferId: string;
  quantity: number;
  theater: any;
  userName: string;
  venueAddress?: string | null;
  venueDepartmentCode?: string | null;
  venueName: string;
};


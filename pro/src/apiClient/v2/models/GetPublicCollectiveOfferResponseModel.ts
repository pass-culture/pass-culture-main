/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { OfferVenueModel } from './OfferVenueModel';

export type GetPublicCollectiveOfferResponseModel = {
  audioDisabilityCompliant?: boolean | null;
  beginningDatetime: string;
  bookingEmails?: Array<string> | null;
  bookingLimitDatetime: string;
  contactEmail: string;
  contactPhone: string;
  dateCreated: string;
  description?: string | null;
  domains: Array<string>;
  durationMinutes?: number | null;
  educationalInstitution?: string | null;
  educationalPriceDetail?: string | null;
  hasBookingLimitDatetimesPassed: boolean;
  id: number;
  interventionArea: Array<string>;
  isActive?: boolean | null;
  isSoldOut: boolean;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  numberOfTickets: number;
  offerVenue: OfferVenueModel;
  status: string;
  students: Array<string>;
  subcategoryId: string;
  totalPrice: number;
  venueId: number;
  visualDisabilityCompliant?: boolean | null;
};


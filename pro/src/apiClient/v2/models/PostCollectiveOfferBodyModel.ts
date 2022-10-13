/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { OfferVenueModel } from './OfferVenueModel';

export type PostCollectiveOfferBodyModel = {
  audioDisabilityCompliant?: boolean;
  beginningDatetime: string;
  bookingEmails: Array<string>;
  bookingLimitDatetime: string;
  contactEmail: string;
  contactPhone: string;
  description: string;
  domains: Array<number>;
  durationMinutes?: number | null;
  educationalInstitutionId?: number | null;
  educationalPriceDetail?: string | null;
  interventionArea: Array<string>;
  isActive: boolean;
  mentalDisabilityCompliant?: boolean;
  motorDisabilityCompliant?: boolean;
  name: string;
  numberOfTickets: number;
  offerVenue: OfferVenueModel;
  students: Array<string>;
  subcategoryId: string;
  totalPrice: number;
  venueId: number;
  visualDisabilityCompliant?: boolean;
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { OfferVenueModel } from './OfferVenueModel';
import type { StudentLevels } from './StudentLevels';

export type PostCollectiveOfferBodyModel = {
  audioDisabilityCompliant?: boolean;
  beginningDatetime: string;
  bookingEmail?: string | null;
  bookingLimitDatetime: string;
  contactEmail: string;
  contactPhone: string;
  description: string;
  domains: Array<string>;
  durationMinutes?: number | null;
  educationalInstitutionId?: number | null;
  educationalPriceDetail?: string | null;
  interventionArea: Array<string>;
  mentalDisabilityCompliant?: boolean;
  motorDisabilityCompliant?: boolean;
  name: string;
  numberOfTickets: number;
  offerVenue: OfferVenueModel;
  students: Array<StudentLevels>;
  subcategoryId: string;
  totalPrice: number;
  venueId: number;
  visualDisabilityCompliant?: boolean;
};


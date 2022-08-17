/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { OfferAddressType } from './OfferAddressType';
import type { StudentLevels } from './StudentLevels';

export type PostCollectiveOfferBodyModel = {
  address?: string | null;
  audioDisabilityCompliant?: boolean;
  beginningDatetime: string;
  bookingEmail?: string | null;
  bookingLimitDatetime: string;
  contactEmail: string;
  contactPhone: string;
  description?: string | null;
  domains: Array<string>;
  durationMinutes?: number | null;
  educationalInstitutionId?: number | null;
  interventionArea: Array<string>;
  mentalDisabilityCompliant?: boolean;
  motorDisabilityCompliant?: boolean;
  name: string;
  numberOfTickets: number;
  offerVenue: OfferAddressType;
  priceDetail?: string | null;
  students: Array<StudentLevels>;
  subcategoryId: string;
  totalPrice: number;
  venueId: number;
  visualDisabilityCompliant?: boolean;
};


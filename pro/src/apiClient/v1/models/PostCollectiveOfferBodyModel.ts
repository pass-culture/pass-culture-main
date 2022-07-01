/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveOfferVenueBodyModel } from './CollectiveOfferVenueBodyModel';
import type { StudentLevels } from './StudentLevels';

export type PostCollectiveOfferBodyModel = {
  audioDisabilityCompliant?: boolean;
  bookingEmail?: string | null;
  contactEmail: string;
  contactPhone: string;
  description?: string | null;
  domains?: Array<number> | null;
  durationMinutes?: number | null;
  mentalDisabilityCompliant?: boolean;
  motorDisabilityCompliant?: boolean;
  name: string;
  offerVenue: CollectiveOfferVenueBodyModel;
  offererId: string;
  students: Array<StudentLevels>;
  subcategoryId: string;
  venueId: string;
  visualDisabilityCompliant?: boolean;
};


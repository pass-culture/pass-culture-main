/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveOfferVenueBodyModel } from './CollectiveOfferVenueBodyModel';
import type { StudentLevels } from './StudentLevels';

export type PostCollectiveOfferBodyModel = {
  audioDisabilityCompliant?: boolean;
  bookingEmails: Array<string>;
  contactEmail: string;
  contactPhone: string;
  description?: string | null;
  domains: Array<number>;
  durationMinutes?: number | null;
  interventionArea?: Array<string> | null;
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


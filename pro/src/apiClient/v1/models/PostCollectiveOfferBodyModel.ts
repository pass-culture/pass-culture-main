/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveOfferVenueBodyModel } from './CollectiveOfferVenueBodyModel';
import type { StudentLevels } from './StudentLevels';

export type PostCollectiveOfferBodyModel = {
  audioDisabilityCompliant?: boolean;
  bookingEmails: Array<string>;
  contactEmail: string;
  contactPhone?: string | null;
  description: string;
  domains?: Array<number> | null;
  durationMinutes?: number | null;
  interventionArea?: Array<string> | null;
  mentalDisabilityCompliant?: boolean;
  motorDisabilityCompliant?: boolean;
  name: string;
  offerVenue: CollectiveOfferVenueBodyModel;
  offererId?: string | null;
  students: Array<StudentLevels>;
  subcategoryId: string;
  templateId?: number | null;
  venueId: number;
  visualDisabilityCompliant?: boolean;
};


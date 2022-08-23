/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { OfferVenueModel } from './OfferVenueModel';
import type { StudentLevels } from './StudentLevels';

export type PatchCollectiveOfferBodyModel = {
  beginningDatetime?: string | null;
  bookingEmail?: string | null;
  bookingLimitDatetime?: string | null;
  contactEmail?: string | null;
  contactPhone?: string | null;
  description?: string | null;
  domains?: Array<string> | null;
  durationMinutes?: number | null;
  educationalInstitutionId?: number | null;
  educationalPriceDetail?: string | null;
  interventionArea?: Array<string> | null;
  name?: string | null;
  numberOfTickets?: number | null;
  offerVenue?: OfferVenueModel | null;
  priceDetail?: string | null;
  students?: Array<StudentLevels> | null;
  subcategoryId?: string | null;
  totalPrice?: number | null;
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveOfferVenueBodyModel } from './CollectiveOfferVenueBodyModel';
import type { StudentLevels } from './StudentLevels';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';

export type PatchCollectiveOfferTemplateBodyModel = {
  audioDisabilityCompliant?: boolean | null;
  bookingEmail?: string | null;
  contactEmail?: string | null;
  contactPhone?: string | null;
  description?: string | null;
  domains?: Array<number> | null;
  durationMinutes?: number | null;
  interventionArea?: Array<string> | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name?: string | null;
  offerVenue?: CollectiveOfferVenueBodyModel | null;
  priceDetail?: string | null;
  students?: Array<StudentLevels> | null;
  subcategoryId?: SubcategoryIdEnum | null;
  visualDisabilityCompliant?: boolean | null;
};


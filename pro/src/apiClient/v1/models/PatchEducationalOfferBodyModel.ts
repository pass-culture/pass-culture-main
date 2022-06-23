/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EducationalOfferPartialExtraDataBodyModel } from './EducationalOfferPartialExtraDataBodyModel';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';

export type PatchEducationalOfferBodyModel = {
  audioDisabilityCompliant?: boolean | null;
  bookingEmail?: string | null;
  description?: string | null;
  durationMinutes?: number | null;
  extraData?: EducationalOfferPartialExtraDataBodyModel | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name?: string | null;
  subcategoryId?: SubcategoryIdEnum | null;
  visualDisabilityCompliant?: boolean | null;
};


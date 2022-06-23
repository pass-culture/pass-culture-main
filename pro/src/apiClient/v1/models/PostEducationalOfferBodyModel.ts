/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { PostEducationalOfferExtraDataBodyModel } from './PostEducationalOfferExtraDataBodyModel';
import type { WithdrawalTypeEnum } from './WithdrawalTypeEnum';

export type PostEducationalOfferBodyModel = {
  audioDisabilityCompliant?: boolean;
  bookingEmail?: string | null;
  description?: string | null;
  durationMinutes?: number | null;
  extraData: PostEducationalOfferExtraDataBodyModel;
  mentalDisabilityCompliant?: boolean;
  motorDisabilityCompliant?: boolean;
  name: string;
  offererId: string;
  subcategoryId: string;
  venueId: string;
  visualDisabilityCompliant?: boolean;
  withdrawalDelay?: number | null;
  withdrawalType?: WithdrawalTypeEnum | null;
};


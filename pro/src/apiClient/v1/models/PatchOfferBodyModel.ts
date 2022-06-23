/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { WithdrawalTypeEnum } from './WithdrawalTypeEnum';

export type PatchOfferBodyModel = {
  ageMax?: number | null;
  ageMin?: number | null;
  audioDisabilityCompliant?: boolean | null;
  bookingEmail?: string | null;
  conditions?: string | null;
  description?: string | null;
  durationMinutes?: number | null;
  externalTicketOfficeUrl?: string | null;
  extraData?: any;
  isActive?: boolean | null;
  isDuo?: boolean | null;
  isNational?: boolean | null;
  mediaUrls?: Array<string> | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name?: string | null;
  productId?: string | null;
  url?: string | null;
  venueId?: string | null;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDelay?: number | null;
  withdrawalDetails?: string | null;
  withdrawalType?: WithdrawalTypeEnum | null;
};


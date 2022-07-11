/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { WithdrawalTypeEnum } from './WithdrawalTypeEnum';

export type PostOfferBodyModel = {
  ageMax?: number | null;
  ageMin?: number | null;
  audioDisabilityCompliant?: boolean;
  bookingEmail?: string | null;
  conditions?: string | null;
  description?: string | null;
  durationMinutes?: number | null;
  externalTicketOfficeUrl?: string | null;
  extraData?: any;
  isDuo?: boolean | null;
  isEducational?: boolean | null;
  isNational?: boolean | null;
  mediaUrls?: Array<string> | null;
  mentalDisabilityCompliant?: boolean;
  motorDisabilityCompliant?: boolean;
  name?: string | null;
  offererId?: string | null;
  productId?: string | null;
  subcategoryId: string;
  url?: string | null;
  venueId: string;
  visualDisabilityCompliant?: boolean;
  withdrawalDelay?: number | null;
  withdrawalDetails?: string | null;
  withdrawalType?: WithdrawalTypeEnum | null;
};


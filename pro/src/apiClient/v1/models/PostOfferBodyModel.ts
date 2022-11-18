/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { WithdrawalTypeEnum } from './WithdrawalTypeEnum';

export type PostOfferBodyModel = {
  audioDisabilityCompliant: boolean;
  bookingEmail?: string | null;
  description?: string | null;
  durationMinutes?: number | null;
  externalTicketOfficeUrl?: string | null;
  extraData?: any;
  isDuo?: boolean | null;
  isNational?: boolean | null;
  mentalDisabilityCompliant: boolean;
  motorDisabilityCompliant: boolean;
  name: string;
  subcategoryId: string;
  url?: string | null;
  venueId: string;
  visualDisabilityCompliant: boolean;
  withdrawalDelay?: number | null;
  withdrawalDetails?: string | null;
  withdrawalType?: WithdrawalTypeEnum | null;
};


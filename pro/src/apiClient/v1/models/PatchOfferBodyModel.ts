/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LocationBodyModel } from './LocationBodyModel';
import type { LocationOnlyOnVenueBodyModel } from './LocationOnlyOnVenueBodyModel';
import type { WithdrawalTypeEnum } from './WithdrawalTypeEnum';
export type PatchOfferBodyModel = {
  audioDisabilityCompliant?: boolean | null;
  bookingAllowedDatetime?: string | null;
  bookingContact?: string | null;
  bookingEmail?: string | null;
  description?: string | null;
  durationMinutes?: number | null;
  externalTicketOfficeUrl?: string | null;
  extraData?: any;
  isDuo?: boolean | null;
  isNational?: boolean | null;
  location?: (LocationBodyModel | LocationOnlyOnVenueBodyModel) | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name?: string | null;
  publicationDatetime?: (string | 'now') | null;
  shouldSendMail?: boolean | null;
  subcategoryId?: string | null;
  url?: string | null;
  videoUrl?: string | null;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDelay?: number | null;
  withdrawalDetails?: string | null;
  withdrawalType?: WithdrawalTypeEnum | null;
};


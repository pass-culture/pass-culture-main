/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AddressBodyModel } from './AddressBodyModel';
import type { WithdrawalTypeEnum } from './WithdrawalTypeEnum';
export type PatchOfferBodyModel = {
  address?: AddressBodyModel | null;
  audioDisabilityCompliant?: boolean | null;
  bookingAllowedDatetime?: string | null;
  bookingContact?: string | null;
  bookingEmail?: string | null;
  description?: string | null;
  durationMinutes?: number | null;
  externalTicketOfficeUrl?: string | null;
  extraData?: any;
  isActive?: boolean | null;
  isDuo?: boolean | null;
  isNational?: boolean | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name?: string | null;
  publicationDatetime?: (string | 'now') | null;
  shouldSendMail?: boolean | null;
  url?: string | null;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDelay?: number | null;
  withdrawalDetails?: string | null;
  withdrawalType?: WithdrawalTypeEnum | null;
};


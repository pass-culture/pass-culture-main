/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WithdrawalTypeEnum } from './WithdrawalTypeEnum';
export type PatchDraftOfferUsefulInformationsBodyModel = {
  audioDisabilityCompliant?: boolean | null;
  bookingContact?: string | null;
  bookingEmail?: string | null;
  durationMinutes?: number | null;
  externalTicketOfficeUrl?: string | null;
  extraData?: any;
  isDuo?: boolean | null;
  isNational?: boolean | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  shouldSendMail?: boolean | null;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDelay?: number | null;
  withdrawalDetails?: string | null;
  withdrawalType?: WithdrawalTypeEnum | null;
};


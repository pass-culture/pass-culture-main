/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PostOfferOffererAddressBodyModel } from './PostOfferOffererAddressBodyModel';
import type { WithdrawalTypeEnum } from './WithdrawalTypeEnum';
export type PostOfferBodyModel = {
  address?: PostOfferOffererAddressBodyModel | null;
  audioDisabilityCompliant: boolean;
  bookingContact?: string | null;
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
  venueId: number;
  visualDisabilityCompliant: boolean;
  withdrawalDelay?: number | null;
  withdrawalDetails?: string | null;
  withdrawalType?: WithdrawalTypeEnum | null;
};


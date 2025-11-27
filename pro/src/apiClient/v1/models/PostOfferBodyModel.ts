/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LocationBodyModel } from './LocationBodyModel';
import type { LocationOnlyOnVenueBodyModel } from './LocationOnlyOnVenueBodyModel';
import type { WithdrawalTypeEnum } from './WithdrawalTypeEnum';
export type PostOfferBodyModel = {
  address?: (LocationBodyModel | LocationOnlyOnVenueBodyModel) | null;
  audioDisabilityCompliant: boolean;
  bookingContact?: string | null;
  bookingEmail?: string | null;
  description?: string | null;
  durationMinutes?: number | null;
  externalTicketOfficeUrl?: string | null;
  extraData?: Record<string, any> | null;
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


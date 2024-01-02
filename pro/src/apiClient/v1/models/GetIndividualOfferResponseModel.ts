/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { GetOfferLastProviderResponseModel } from './GetOfferLastProviderResponseModel';
import type { GetOfferMediationResponseModel } from './GetOfferMediationResponseModel';
import type { GetOfferVenueResponseModel } from './GetOfferVenueResponseModel';
import type { OfferStatus } from './OfferStatus';
import type { PriceCategoryResponseModel } from './PriceCategoryResponseModel';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';
import type { WithdrawalTypeEnum } from './WithdrawalTypeEnum';

export type GetIndividualOfferResponseModel = {
  activeMediation?: GetOfferMediationResponseModel | null;
  audioDisabilityCompliant?: boolean | null;
  bookingContact?: string | null;
  bookingEmail?: string | null;
  bookingsCount?: number | null;
  dateCreated: string;
  description?: string | null;
  durationMinutes?: number | null;
  externalTicketOfficeUrl?: string | null;
  extraData?: any;
  hasBookingLimitDatetimesPassed: boolean;
  hasStocks: boolean;
  id: number;
  isActivable: boolean;
  isActive: boolean;
  isDigital: boolean;
  isDuo: boolean;
  isEditable: boolean;
  isEvent: boolean;
  isNational: boolean;
  isNonFreeOffer?: boolean | null;
  isThing: boolean;
  lastProvider?: GetOfferLastProviderResponseModel | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  priceCategories?: Array<PriceCategoryResponseModel> | null;
  status: OfferStatus;
  subcategoryId: SubcategoryIdEnum;
  thumbUrl?: string | null;
  url?: string | null;
  venue: GetOfferVenueResponseModel;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDelay?: number | null;
  withdrawalDetails?: string | null;
  withdrawalType?: WithdrawalTypeEnum | null;
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { GetOfferLastProviderResponseModel } from './GetOfferLastProviderResponseModel';
import type { GetOfferMediationResponseModel } from './GetOfferMediationResponseModel';
import type { GetOfferStockResponseModel } from './GetOfferStockResponseModel';
import type { GetOfferVenueResponseModel } from './GetOfferVenueResponseModel';
import type { OfferStatus } from './OfferStatus';
import type { PriceCategoryResponseModel } from './PriceCategoryResponseModel';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';
import type { WithdrawalTypeEnum } from './WithdrawalTypeEnum';

export type GetIndividualOfferResponseModel = {
  activeMediation?: GetOfferMediationResponseModel | null;
  audioDisabilityCompliant?: boolean | null;
  bookingEmail?: string | null;
  dateCreated: string;
  description?: string | null;
  durationMinutes?: number | null;
  externalTicketOfficeUrl?: string | null;
  extraData?: any;
  hasBookingLimitDatetimesPassed: boolean;
  isActive: boolean;
  isDigital: boolean;
  isDuo: boolean;
  isEditable: boolean;
  isEducational: boolean;
  isEvent: boolean;
  isNational: boolean;
  isThing: boolean;
  lastProvider?: GetOfferLastProviderResponseModel | null;
  mediaUrls: Array<string>;
  mediations: Array<GetOfferMediationResponseModel>;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  nonHumanizedId: number;
  priceCategories?: Array<PriceCategoryResponseModel> | null;
  status: OfferStatus;
  stocks: Array<GetOfferStockResponseModel>;
  subcategoryId: SubcategoryIdEnum;
  thumbUrl?: string | null;
  url?: string | null;
  venue: GetOfferVenueResponseModel;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDelay?: number | null;
  withdrawalDetails?: string | null;
  withdrawalType?: WithdrawalTypeEnum | null;
};


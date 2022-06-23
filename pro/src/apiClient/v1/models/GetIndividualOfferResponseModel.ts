/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { GetOfferLastProviderResponseModel } from './GetOfferLastProviderResponseModel';
import type { GetOfferMediationResponseModel } from './GetOfferMediationResponseModel';
import type { GetOfferProductResponseModel } from './GetOfferProductResponseModel';
import type { GetOfferStockResponseModel } from './GetOfferStockResponseModel';
import type { GetOfferVenueResponseModel } from './GetOfferVenueResponseModel';
import type { OfferStatus } from './OfferStatus';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';
import type { WithdrawalTypeEnum } from './WithdrawalTypeEnum';

export type GetIndividualOfferResponseModel = {
  activeMediation?: GetOfferMediationResponseModel | null;
  ageMax?: number | null;
  ageMin?: number | null;
  audioDisabilityCompliant?: boolean | null;
  bookingEmail?: string | null;
  conditions?: string | null;
  dateCreated: string;
  dateModifiedAtLastProvider?: string | null;
  dateRange: Array<string>;
  description?: string | null;
  durationMinutes?: number | null;
  externalTicketOfficeUrl?: string | null;
  extraData?: any;
  fieldsUpdated: Array<string>;
  hasBookingLimitDatetimesPassed: boolean;
  id: string;
  isActive: boolean;
  isBookable: boolean;
  isDigital: boolean;
  isDuo: boolean;
  isEditable: boolean;
  isEducational: boolean;
  isEvent: boolean;
  isNational: boolean;
  isThing: boolean;
  lastProvider?: GetOfferLastProviderResponseModel | null;
  lastProviderId?: string | null;
  mediaUrls: Array<string>;
  mediations: Array<GetOfferMediationResponseModel>;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  nonHumanizedId: number;
  product: GetOfferProductResponseModel;
  productId: string;
  status: OfferStatus;
  stocks: Array<GetOfferStockResponseModel>;
  subcategoryId: SubcategoryIdEnum;
  thumbUrl?: string | null;
  url?: string | null;
  venue: GetOfferVenueResponseModel;
  venueId: string;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDelay?: number | null;
  withdrawalDetails?: string | null;
  withdrawalType?: WithdrawalTypeEnum | null;
};


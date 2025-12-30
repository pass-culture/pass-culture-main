/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ArtistOfferResponseModel } from './ArtistOfferResponseModel';
import type { GetOfferLastProviderResponseModel } from './GetOfferLastProviderResponseModel';
import type { GetOfferMediationResponseModel } from './GetOfferMediationResponseModel';
import type { GetOfferVenueResponseModel } from './GetOfferVenueResponseModel';
import type { LocationResponseModel } from './LocationResponseModel';
import type { OfferStatus } from './OfferStatus';
import type { PriceCategoryResponseModel } from './PriceCategoryResponseModel';
import type { ShortHighlightResponseModel } from './ShortHighlightResponseModel';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';
import type { VideoData } from './VideoData';
import type { WithdrawalTypeEnum } from './WithdrawalTypeEnum';
export type GetIndividualOfferWithAddressResponseModel = {
  activeMediation?: GetOfferMediationResponseModel | null;
  artistOfferLinks: Array<ArtistOfferResponseModel>;
  audioDisabilityCompliant?: boolean | null;
  bookingAllowedDatetime?: string | null;
  bookingContact?: string | null;
  bookingEmail?: string | null;
  bookingsCount?: number | null;
  canBeEvent: boolean;
  dateCreated: string;
  description?: string | null;
  durationMinutes?: number | null;
  externalTicketOfficeUrl?: string | null;
  extraData?: any;
  hasBookingLimitDatetimesPassed: boolean;
  hasPendingBookings: boolean;
  hasStocks: boolean;
  highlightRequests: Array<ShortHighlightResponseModel>;
  id: number;
  isActive: boolean;
  isDigital: boolean;
  isDuo: boolean;
  isEditable: boolean;
  isEvent: boolean;
  isHeadlineOffer: boolean;
  isNational: boolean;
  isNonFreeOffer?: boolean | null;
  isThing: boolean;
  lastProvider?: GetOfferLastProviderResponseModel | null;
  location?: LocationResponseModel | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  priceCategories?: Array<PriceCategoryResponseModel> | null;
  productId?: number | null;
  publicationDate?: string | null;
  publicationDatetime?: string | null;
  status: OfferStatus;
  subcategoryId: SubcategoryIdEnum;
  thumbUrl?: string | null;
  url?: string | null;
  venue: GetOfferVenueResponseModel;
  videoData: VideoData;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDelay?: number | null;
  withdrawalDetails?: string | null;
  withdrawalType?: WithdrawalTypeEnum | null;
};


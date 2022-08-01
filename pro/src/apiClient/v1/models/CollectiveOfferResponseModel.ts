/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveOffersStockResponseModel } from './CollectiveOffersStockResponseModel';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';
import type { ListOffersVenueResponseModel } from './ListOffersVenueResponseModel';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';

export type CollectiveOfferResponseModel = {
  educationalInstitution?: EducationalInstitutionResponseModel | null;
  hasBookingLimitDatetimesPassed: boolean;
  id: string;
  interventionArea: Array<string>;
  isActive: boolean;
  isEditable: boolean;
  isEducational: boolean;
  isEvent: boolean;
  isShowcase?: boolean | null;
  isThing: boolean;
  name: string;
  offerId?: string | null;
  productIsbn?: string | null;
  status: string;
  stocks: Array<CollectiveOffersStockResponseModel>;
  subcategoryId: SubcategoryIdEnum;
  thumbUrl?: string | null;
  venue: ListOffersVenueResponseModel;
  venueId: string;
};


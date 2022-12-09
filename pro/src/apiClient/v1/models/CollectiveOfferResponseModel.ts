/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveOffersBookingResponseModel } from './CollectiveOffersBookingResponseModel';
import type { CollectiveOffersStockResponseModel } from './CollectiveOffersStockResponseModel';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';
import type { ListOffersVenueResponseModel } from './ListOffersVenueResponseModel';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';

export type CollectiveOfferResponseModel = {
  booking?: CollectiveOffersBookingResponseModel | null;
  educationalInstitution?: EducationalInstitutionResponseModel | null;
  hasBookingLimitDatetimesPassed: boolean;
  id: string;
  imageCredit?: string | null;
  imageUrl?: string | null;
  interventionArea: Array<string>;
  isActive: boolean;
  isEditable: boolean;
  isEducational: boolean;
  isShowcase: boolean;
  name: string;
  status: string;
  stocks: Array<CollectiveOffersStockResponseModel>;
  subcategoryId: SubcategoryIdEnum;
  templateId?: string | null;
  venue: ListOffersVenueResponseModel;
  venueId: string;
};


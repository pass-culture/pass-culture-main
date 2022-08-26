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
  isShowcase: boolean;
  name: string;
  status: string;
  stocks: Array<CollectiveOffersStockResponseModel>;
  subcategoryId: SubcategoryIdEnum;
  venue: ListOffersVenueResponseModel;
  venueId: string;
};


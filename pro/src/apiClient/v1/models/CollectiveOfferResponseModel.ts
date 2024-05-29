/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOffersBookingResponseModel } from './CollectiveOffersBookingResponseModel';
import type { CollectiveOffersStockResponseModel } from './CollectiveOffersStockResponseModel';
import type { EacFormat } from './EacFormat';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';
import type { ListOffersVenueResponseModel } from './ListOffersVenueResponseModel';
import type { NationalProgramModel } from './NationalProgramModel';
import type { OfferStatus } from './OfferStatus';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';
export type CollectiveOfferResponseModel = {
  booking?: CollectiveOffersBookingResponseModel | null;
  educationalInstitution?: EducationalInstitutionResponseModel | null;
  formats?: Array<EacFormat> | null;
  hasBookingLimitDatetimesPassed: boolean;
  id: number;
  imageCredit?: string | null;
  imageUrl?: string | null;
  interventionArea: Array<string>;
  isActive: boolean;
  isEditable: boolean;
  isEducational: boolean;
  isPublicApi: boolean;
  isShowcase: boolean;
  name: string;
  nationalProgram?: NationalProgramModel | null;
  status: OfferStatus;
  stocks: Array<CollectiveOffersStockResponseModel>;
  subcategoryId?: (SubcategoryIdEnum | string) | null;
  templateId?: string | null;
  venue: ListOffersVenueResponseModel;
};


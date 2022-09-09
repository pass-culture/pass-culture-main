/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export { AppClientV2 } from './AppClientV2';

export { ApiError } from './core/ApiError';
export { BaseHttpRequest } from './core/BaseHttpRequest';
export { CancelablePromise, CancelError } from './core/CancelablePromise';
export { OpenAPI } from './core/OpenAPI';
export type { OpenAPIConfig } from './core/OpenAPI';

export type { AuthErrorResponseModel } from './models/AuthErrorResponseModel';
export { BookingFormula } from './models/BookingFormula';
export { BookingOfferType } from './models/BookingOfferType';
export type { CollectiveOffersCategoryResponseModel } from './models/CollectiveOffersCategoryResponseModel';
export type { CollectiveOffersDomainResponseModel } from './models/CollectiveOffersDomainResponseModel';
export type { CollectiveOffersEducationalInstitutionResponseModel } from './models/CollectiveOffersEducationalInstitutionResponseModel';
export type { CollectiveOffersListCategoriesResponseModel } from './models/CollectiveOffersListCategoriesResponseModel';
export type { CollectiveOffersListDomainsResponseModel } from './models/CollectiveOffersListDomainsResponseModel';
export type { CollectiveOffersListEducationalInstitutionResponseModel } from './models/CollectiveOffersListEducationalInstitutionResponseModel';
export type { CollectiveOffersListResponseModel } from './models/CollectiveOffersListResponseModel';
export type { CollectiveOffersListStudentLevelsResponseModel } from './models/CollectiveOffersListStudentLevelsResponseModel';
export type { CollectiveOffersListSubCategoriesResponseModel } from './models/CollectiveOffersListSubCategoriesResponseModel';
export type { CollectiveOffersListVenuesResponseModel } from './models/CollectiveOffersListVenuesResponseModel';
export type { CollectiveOffersResponseModel } from './models/CollectiveOffersResponseModel';
export type { CollectiveOffersStudentLevelResponseModel } from './models/CollectiveOffersStudentLevelResponseModel';
export type { CollectiveOffersSubCategoryResponseModel } from './models/CollectiveOffersSubCategoryResponseModel';
export type { CollectiveOffersVenueResponseModel } from './models/CollectiveOffersVenueResponseModel';
export type { ErrorResponseModel } from './models/ErrorResponseModel';
export type { GetBookingResponse } from './models/GetBookingResponse';
export type { GetListEducationalInstitutionsQueryModel } from './models/GetListEducationalInstitutionsQueryModel';
export type { GetPublicCollectiveOfferResponseModel } from './models/GetPublicCollectiveOfferResponseModel';
export type { ListCollectiveOffersQueryModel } from './models/ListCollectiveOffersQueryModel';
export { OfferAddressType } from './models/OfferAddressType';
export { OfferStatus } from './models/OfferStatus';
export type { OfferVenueModel } from './models/OfferVenueModel';
export type { PatchCollectiveOfferBodyModel } from './models/PatchCollectiveOfferBodyModel';
export type { PostCollectiveOfferBodyModel } from './models/PostCollectiveOfferBodyModel';
export { StudentLevels } from './models/StudentLevels';
export type { UpdateVenueStockBodyModel } from './models/UpdateVenueStockBodyModel';
export type { UpdateVenueStocksBodyModel } from './models/UpdateVenueStocksBodyModel';
export type { ValidationError } from './models/ValidationError';
export type { ValidationErrorElement } from './models/ValidationErrorElement';

export { ApiContremarqueService } from './services/ApiContremarqueService';
export { ApiOffresCollectivesService } from './services/ApiOffresCollectivesService';
export { ApiStocksService } from './services/ApiStocksService';

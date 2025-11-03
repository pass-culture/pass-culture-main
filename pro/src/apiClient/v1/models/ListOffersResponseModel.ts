/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ListOffersOfferResponseModel } from './ListOffersOfferResponseModel';
export type ListOffersResponseModel = {
  has_next: boolean;
  has_prev: boolean;
  offers: Array<ListOffersOfferResponseModel>;
  pages: number;
  total: number;
};


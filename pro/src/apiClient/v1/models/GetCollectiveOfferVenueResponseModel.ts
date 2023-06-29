/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { GetCollectiveOfferManagingOffererResponseModel } from './GetCollectiveOfferManagingOffererResponseModel';

export type GetCollectiveOfferVenueResponseModel = {
  departementCode?: string | null;
  id: number;
  managingOfferer: GetCollectiveOfferManagingOffererResponseModel;
  name: string;
  publicName?: string | null;
};


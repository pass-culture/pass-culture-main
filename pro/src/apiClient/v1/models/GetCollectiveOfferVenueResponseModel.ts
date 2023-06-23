/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { GetCollectiveOfferManagingOffererResponseModel } from './GetCollectiveOfferManagingOffererResponseModel';

export type GetCollectiveOfferVenueResponseModel = {
  departementCode?: string | null;
  managingOfferer: GetCollectiveOfferManagingOffererResponseModel;
  name: string;
  nonHumanizedId: number;
  publicName?: string | null;
};


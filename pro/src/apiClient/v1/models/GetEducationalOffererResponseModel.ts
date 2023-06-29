/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { GetEducationalOffererVenueResponseModel } from './GetEducationalOffererVenueResponseModel';

export type GetEducationalOffererResponseModel = {
  id: number;
  managedVenues: Array<GetEducationalOffererVenueResponseModel>;
  name: string;
};


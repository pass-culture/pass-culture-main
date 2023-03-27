/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { StockCreationBodyModel } from './StockCreationBodyModel';
import type { StockEditionBodyModel } from './StockEditionBodyModel';

export type StocksUpsertBodyModel = {
  offerId: number;
  stocks: Array<(StockCreationBodyModel | StockEditionBodyModel)>;
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { StockCreationBodyModel } from './StockCreationBodyModel';
import type { StockEditionBodyModel } from './StockEditionBodyModel';

export type StocksUpsertBodyModel = {
  humanizedOfferId: string;
  stocks: Array<(StockCreationBodyModel | StockEditionBodyModel)>;
};


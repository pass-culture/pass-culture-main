/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Address } from './Address';

export type SiretInfo = {
  active: boolean;
  address: Address;
  ape_code: string;
  legal_category_code: string;
  name: string;
  siret: string;
};

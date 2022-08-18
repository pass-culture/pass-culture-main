/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { OfferAddressType } from './OfferAddressType';

export type OfferVenueModel = {
  addressType: OfferAddressType;
  otherAddress?: string | null;
  venueId?: number | null;
};


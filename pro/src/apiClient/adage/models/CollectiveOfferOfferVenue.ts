/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { OfferAddressType } from './OfferAddressType';

export type CollectiveOfferOfferVenue = {
  address?: string | null;
  addressType: OfferAddressType;
  city?: string | null;
  name?: string | null;
  otherAddress: string;
  postalCode?: string | null;
  publicName?: string | null;
  venueId?: number | null;
};


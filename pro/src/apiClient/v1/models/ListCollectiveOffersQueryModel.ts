/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveLocationType } from './CollectiveLocationType';
import type { CollectiveOfferDisplayedStatus } from './CollectiveOfferDisplayedStatus';
import type { EacFormat } from './EacFormat';
export type ListCollectiveOffersQueryModel = {
  format?: (EacFormat | null);
  locationType?: (CollectiveLocationType | null);
  name?: (string | null);
  offererAddressId?: (number | null);
  offererId?: (number | null);
  periodBeginningDate?: (string | null);
  periodEndingDate?: (string | null);
  status?: (Array<CollectiveOfferDisplayedStatus> | null);
  venueId?: (number | null);
};


/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveAndIndividualRevenue } from './CollectiveAndIndividualRevenue';
import type { CollectiveRevenue } from './CollectiveRevenue';
import type { IndividualRevenue } from './IndividualRevenue';
export type AggregatedRevenue = {
  expectedRevenue?: (CollectiveAndIndividualRevenue | CollectiveRevenue | IndividualRevenue);
  revenue: (CollectiveAndIndividualRevenue | CollectiveRevenue | IndividualRevenue);
};


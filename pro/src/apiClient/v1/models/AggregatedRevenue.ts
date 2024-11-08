/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOnlyRevenue } from './CollectiveOnlyRevenue';
import type { IndividualOnlyRevenue } from './IndividualOnlyRevenue';
import type { Revenue } from './Revenue';
export type AggregatedRevenue = {
  expectedRevenue: (Revenue | IndividualOnlyRevenue | CollectiveOnlyRevenue);
  revenue: (Revenue | IndividualOnlyRevenue | CollectiveOnlyRevenue);
};


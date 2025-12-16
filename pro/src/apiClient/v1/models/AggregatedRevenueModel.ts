/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveRevenue } from './CollectiveRevenue';
import type { IndividualRevenue } from './IndividualRevenue';
import type { TotalRevenue } from './TotalRevenue';
export type AggregatedRevenueModel = {
  expectedRevenue?: (CollectiveRevenue | IndividualRevenue | TotalRevenue | null);
  revenue: (CollectiveRevenue | IndividualRevenue | TotalRevenue);
};


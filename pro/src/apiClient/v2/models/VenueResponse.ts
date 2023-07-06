/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { PartialAccessibility } from './PartialAccessibility';
import type { VenueDigitalLocation } from './VenueDigitalLocation';
import type { VenuePhysicalLocation } from './VenuePhysicalLocation';
import type { VenueTypeEnum } from './VenueTypeEnum';

export type VenueResponse = {
  accessibility: PartialAccessibility;
  activityDomain: VenueTypeEnum;
  createdDatetime: string;
  id: number;
  legalName: string;
  /**
   * Location where the offers will be available or will take place. There is exactly one digital venue per offerer, which is listed although its id is not required to create a digital offer (see DigitalLocation model).
   */
  location: (VenuePhysicalLocation | VenueDigitalLocation);
  /**
   * If null, legalName is used.
   */
  publicName: string | null;
  /**
   * Null when venue is digital or when siretComment field is not null.
   */
  siret?: string | null;
  /**
   * Applicable if siret is null and venue is physical.
   */
  siretComment?: string | null;
};


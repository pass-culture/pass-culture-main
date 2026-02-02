/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ActivityNotOpenToPublic } from './ActivityNotOpenToPublic';
import type { ActivityOpenToPublic } from './ActivityOpenToPublic';
import type { LocationBodyModel } from './LocationBodyModel';
import type { Target } from './Target';
export type SaveNewOnboardingDataQueryModel = {
  activity: (ActivityOpenToPublic | ActivityNotOpenToPublic);
  address: LocationBodyModel;
  createVenueWithoutSiret?: boolean;
  culturalDomains?: Array<string> | null;
  isOpenToPublic: boolean;
  phoneNumber?: string | null;
  publicName?: string | null;
  siret: string;
  target: Target;
  token: string;
  webPresence: string;
};


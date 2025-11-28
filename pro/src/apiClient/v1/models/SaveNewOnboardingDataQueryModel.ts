/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LocationBodyModel } from './LocationBodyModel';
import type { OnboardingActivity } from './OnboardingActivity';
import type { Target } from './Target';
export type SaveNewOnboardingDataQueryModel = {
  activity?: OnboardingActivity | null;
  address: LocationBodyModel;
  createVenueWithoutSiret?: boolean;
  isOpenToPublic: boolean;
  phoneNumber?: string | null;
  publicName?: string | null;
  siret: string;
  target: Target;
  token: string;
  venueTypeCode?: string | null;
  webPresence: string;
};


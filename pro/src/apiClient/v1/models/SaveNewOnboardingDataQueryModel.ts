/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Target } from './Target';
export type SaveNewOnboardingDataQueryModel = {
  address?: string | null;
  banId?: string | null;
  city: string;
  createVenueWithoutSiret?: boolean;
  latitude: number;
  longitude: number;
  postalCode: string;
  publicName?: string | null;
  siret: string;
  target: Target;
  token: string;
  venueTypeCode: string;
  webPresence: string;
};


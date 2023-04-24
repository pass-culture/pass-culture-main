/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Target } from './Target';

export type SaveNewOnboardingDataQueryModel = {
  address: string;
  city: string;
  createVenueWithoutSiret?: boolean;
  latitude: number;
  longitude: number;
  postalCode: string;
  publicName?: string | null;
  siret: string;
  target: Target;
  venueTypeCode: string;
  webPresence: string;
};


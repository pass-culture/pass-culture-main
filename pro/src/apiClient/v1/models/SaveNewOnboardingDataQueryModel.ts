/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Target } from './Target';

export type SaveNewOnboardingDataQueryModel = {
  createVenueWithoutSiret?: boolean;
  publicName?: string | null;
  siret: string;
  target: Target;
  venueTypeCode: string;
  webPresence: string;
};


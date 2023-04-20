/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Target } from './Target';

export type SaveNewOnboardingDataQueryModel = {
  createVenueWithoutSiret?: boolean;
  name?: string | null;
  publicName?: string | null;
  siret: string;
  target: Target;
  venueType?: string | null;
  venueTypeCode: string;
  webPresence: string;
};


/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Target } from './Target';
import type { VenueTypeCode } from './VenueTypeCode';

export type SaveNewOnboardingDataQueryModel = {
  createVenueWithoutSiret?: boolean;
  name?: string | null;
  publicName?: string | null;
  siret: string;
  target: Target;
  venueType?: string | null;
  venueTypeCode?: keyof typeof VenueTypeCode | null;
  webPresence: string;
};

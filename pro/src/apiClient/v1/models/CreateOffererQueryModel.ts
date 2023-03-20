/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Target } from './Target';

export type CreateOffererQueryModel = {
  address?: string | null;
  city: string;
  latitude?: number | null;
  longitude?: number | null;
  name: string;
  postalCode: string;
  siren: string;
  target?: Target | null;
  venueType?: string | null;
  webPresence?: string | null;
};


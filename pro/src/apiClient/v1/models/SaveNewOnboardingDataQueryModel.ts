/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AddressBodyModel } from './AddressBodyModel';
import type { Target } from './Target';
export type SaveNewOnboardingDataQueryModel = {
  address: AddressBodyModel;
  createVenueWithoutSiret?: boolean;
  isOpenToPublic: boolean;
  phoneNumber?: string | null;
  publicName?: string | null;
  siret: string;
  target: Target;
  token: string;
  venueTypeCode: string;
  webPresence: string;
};


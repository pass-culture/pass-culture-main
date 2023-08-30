/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AdageFrontRoles } from './AdageFrontRoles';
import type { RedactorPreferences } from './RedactorPreferences';

export type AuthenticatedResponse = {
  departmentCode?: string | null;
  email?: string | null;
  institutionCity?: string | null;
  institutionName?: string | null;
  lat?: number | null;
  lon?: number | null;
  preferences?: RedactorPreferences | null;
  role: AdageFrontRoles;
  uai?: string | null;
};


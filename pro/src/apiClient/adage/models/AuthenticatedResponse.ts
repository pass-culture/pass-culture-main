/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { AdageFrontRoles } from './AdageFrontRoles';

export type AuthenticatedResponse = {
  departmentCode?: string | null;
  email?: string | null;
  institutionCity?: string | null;
  institutionName?: string | null;
  role: AdageFrontRoles;
  uai?: string | null;
};


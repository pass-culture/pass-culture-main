/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AdageFrontRoles } from './AdageFrontRoles';
import type { EducationalInstitutionProgramModel } from './EducationalInstitutionProgramModel';
import type { InstitutionRuralLevel } from './InstitutionRuralLevel';
import type { RedactorPreferences } from './RedactorPreferences';
export type AuthenticatedResponse = {
  canPrebook?: boolean | null;
  departmentCode?: string | null;
  email?: string | null;
  favoritesCount?: number;
  institutionCity?: string | null;
  institutionName?: string | null;
  institutionRuralLevel?: InstitutionRuralLevel | null;
  lat?: number | null;
  lon?: number | null;
  offersCount?: number;
  preferences?: RedactorPreferences | null;
  programs?: Array<EducationalInstitutionProgramModel>;
  role: AdageFrontRoles;
  uai?: string | null;
};


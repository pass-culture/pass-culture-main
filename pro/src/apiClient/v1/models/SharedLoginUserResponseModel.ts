/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserRole } from './UserRole';
export type SharedLoginUserResponseModel = {
  activity?: (string | null);
  address?: (string | null);
  city?: (string | null);
  dateCreated: string;
  dateOfBirth?: (string | null);
  departementCode?: (string | null);
  email: string;
  firstName?: (string | null);
  hasUserOfferer?: (boolean | null);
  id: number;
  isEmailValidated: boolean;
  lastConnectionDate?: (string | null);
  lastName?: (string | null);
  needsToFillCulturalSurvey?: (boolean | null);
  phoneNumber?: (string | null);
  postalCode?: (string | null);
  roles: Array<UserRole>;
};


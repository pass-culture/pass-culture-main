/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GenderEnum } from './GenderEnum';
import type { PhoneValidationStatusType } from './PhoneValidationStatusType';
import type { UserRole } from './UserRole';
export type SharedCurrentUserResponseModel = {
  activity?: string | null;
  address?: string | null;
  city?: string | null;
  civility?: GenderEnum | null;
  dateCreated: string;
  dateOfBirth?: string | null;
  departementCode?: string | null;
  email: string;
  externalIds?: Record<string, any> | null;
  firstName?: string | null;
  hasSeenProTutorials?: boolean | null;
  hasUserOfferer?: boolean | null;
  id: number;
  idPieceNumber?: string | null;
  isAdmin: boolean;
  isEmailValidated: boolean;
  isImpersonated?: boolean;
  lastConnectionDate?: string | null;
  lastName?: string | null;
  needsToFillCulturalSurvey?: boolean | null;
  notificationSubscriptions?: Record<string, any> | null;
  phoneNumber?: string | null;
  phoneValidationStatus?: PhoneValidationStatusType | null;
  postalCode?: string | null;
  roles: Array<UserRole>;
};


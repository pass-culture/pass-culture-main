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
  hasPhysicalVenues?: boolean | null;
  hasSeenProRgs?: boolean | null;
  hasSeenProTutorials?: boolean | null;
  idPieceNumber?: string | null;
  isAdmin: boolean;
  isEmailValidated: boolean;
  lastConnectionDate?: string | null;
  lastName?: string | null;
  needsToFillCulturalSurvey?: boolean | null;
  nonHumanizedId: number;
  notificationSubscriptions?: Record<string, any> | null;
  phoneNumber?: string | null;
  phoneValidationStatus?: PhoneValidationStatusType | null;
  postalCode?: string | null;
  roles: Array<UserRole>;
};


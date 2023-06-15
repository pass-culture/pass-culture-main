/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { GenderEnum } from './GenderEnum';
import type { UserRole } from './UserRole';

export type SharedLoginUserResponseModel = {
  activity?: string | null;
  address?: string | null;
  city?: string | null;
  civility?: GenderEnum | null;
  dateCreated: string;
  dateOfBirth?: string | null;
  departementCode?: string | null;
  email: string;
  firstName?: string | null;
  hasPhysicalVenues?: boolean | null;
  hasSeenProRgs?: boolean | null;
  hasSeenProTutorials?: boolean | null;
  isAdmin: boolean;
  isEmailValidated: boolean;
  lastConnectionDate?: string | null;
  lastName?: string | null;
  needsToFillCulturalSurvey?: boolean | null;
  nonHumanizedId: number;
  phoneNumber?: string | null;
  postalCode?: string | null;
  roles: Array<UserRole>;
};


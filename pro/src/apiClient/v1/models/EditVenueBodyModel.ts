/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { StudentLevels } from './StudentLevels';
import type { VenueContactModel } from './VenueContactModel';

export type EditVenueBodyModel = {
  address?: string | null;
  audioDisabilityCompliant?: boolean | null;
  bookingEmail?: string | null;
  businessUnitId?: number | null;
  city?: string | null;
  collectiveAccessInformation?: string | null;
  collectiveDescription?: string | null;
  collectiveDomains?: Array<number> | null;
  collectiveEmail?: string | null;
  collectiveInterventionArea?: Array<string> | null;
  collectiveLegalStatus?: number | null;
  collectiveNetwork?: Array<string> | null;
  collectivePhone?: string | null;
  collectiveStudents?: Array<StudentLevels> | null;
  collectiveWebsite?: string | null;
  comment?: string | null;
  contact?: VenueContactModel | null;
  description?: string | null;
  isAccessibilityAppliedOnAllOffers?: boolean | null;
  isEmailAppliedOnAllOffers?: boolean | null;
  isWithdrawalAppliedOnAllOffers?: boolean | null;
  latitude?: (number | string) | null;
  longitude?: (number | string) | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name?: string | null;
  postalCode?: string | null;
  publicName?: string | null;
  reimbursementPointId?: number | null;
  siret?: string | null;
  venueLabelId?: number | null;
  venueTypeCode?: string | null;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDetails?: string | null;
};


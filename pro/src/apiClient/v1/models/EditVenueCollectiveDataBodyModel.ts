/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { StudentLevels } from './StudentLevels';

export type EditVenueCollectiveDataBodyModel = {
  collectiveAccessInformation?: string | null;
  collectiveDescription?: string | null;
  collectiveDomains?: Array<number> | null;
  collectiveEmail?: string | null;
  collectiveInterventionArea?: Array<string> | null;
  collectiveNetwork?: Array<string> | null;
  collectivePhone?: string | null;
  collectiveStudents?: Array<StudentLevels> | null;
  collectiveWebsite?: string | null;
  venueEducationalStatusId?: number | null;
};


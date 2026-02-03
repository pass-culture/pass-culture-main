/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ActivityNotOpenToPublic } from './ActivityNotOpenToPublic';
import type { ActivityOpenToPublic } from './ActivityOpenToPublic';
import type { StudentLevels } from './StudentLevels';
export type EditVenueCollectiveDataBodyModel = {
  activity?: (ActivityOpenToPublic | ActivityNotOpenToPublic) | null;
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


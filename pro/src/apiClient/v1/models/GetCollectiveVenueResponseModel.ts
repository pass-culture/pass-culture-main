/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { GetVenueDomainResponseModel } from './GetVenueDomainResponseModel';
import type { LegalStatusResponseModel } from './LegalStatusResponseModel';
import type { StudentLevels } from './StudentLevels';

export type GetCollectiveVenueResponseModel = {
  collectiveAccessInformation?: string | null;
  collectiveDescription?: string | null;
  collectiveDomains: Array<GetVenueDomainResponseModel>;
  collectiveEmail?: string | null;
  collectiveInterventionArea?: Array<string> | null;
  collectiveLegalStatus?: LegalStatusResponseModel | null;
  collectiveNetwork?: Array<string> | null;
  collectivePhone?: string | null;
  collectiveStudents?: Array<StudentLevels> | null;
  collectiveWebsite?: string | null;
  id: string;
};


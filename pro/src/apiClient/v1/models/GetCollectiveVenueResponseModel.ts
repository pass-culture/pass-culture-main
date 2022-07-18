/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { GetCollectiveVenueLegalStatusResponseModel } from './GetCollectiveVenueLegalStatusResponseModel';
import type { GetVenueDomainResponseModel } from './GetVenueDomainResponseModel';
import type { StudentLevels } from './StudentLevels';

export type GetCollectiveVenueResponseModel = {
  collectiveAccessInformation?: string | null;
  collectiveDescription?: string | null;
  collectiveDomains: Array<GetVenueDomainResponseModel>;
  collectiveEmail?: string | null;
  collectiveInterventionArea?: Array<string> | null;
  collectiveLegalStatus?: GetCollectiveVenueLegalStatusResponseModel | null;
  collectiveNetwork?: Array<string> | null;
  collectivePhone?: string | null;
  collectiveStudents?: Array<StudentLevels> | null;
  collectiveWebsite?: string | null;
  id: string;
};


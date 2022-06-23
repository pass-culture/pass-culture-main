/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';

export type EducationalInstitutionsResponseModel = {
  educationalInstitutions: Array<EducationalInstitutionResponseModel>;
  page: number;
  pages: number;
  total: number;
};


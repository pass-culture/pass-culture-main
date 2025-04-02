/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferOfferVenue } from './CollectiveOfferOfferVenue';
import type { EacFormat } from './EacFormat';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';
import type { EducationalRedactorResponseModel } from './EducationalRedactorResponseModel';
import type { NationalProgramModel } from './NationalProgramModel';
import type { OfferDomain } from './OfferDomain';
import type { OfferStockResponse } from './OfferStockResponse';
import type { OfferVenueResponse } from './OfferVenueResponse';
import type { StudentLevels } from './StudentLevels';
export type CollectiveOfferResponseModel = {
  audioDisabilityCompliant?: boolean | null;
  contactEmail?: string | null;
  contactPhone?: string | null;
  description?: string | null;
  domains: Array<OfferDomain>;
  durationMinutes?: number | null;
  educationalInstitution?: EducationalInstitutionResponseModel | null;
  educationalPriceDetail?: string | null;
  formats: Array<EacFormat>;
  id: number;
  imageCredit?: string | null;
  imageUrl?: string | null;
  interventionArea: Array<string>;
  isExpired: boolean;
  isSoldOut: boolean;
  isTemplate?: boolean;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  nationalProgram?: NationalProgramModel | null;
  offerVenue: CollectiveOfferOfferVenue;
  stock: OfferStockResponse;
  students: Array<StudentLevels>;
  teacher?: EducationalRedactorResponseModel | null;
  venue: OfferVenueResponse;
  visualDisabilityCompliant?: boolean | null;
};


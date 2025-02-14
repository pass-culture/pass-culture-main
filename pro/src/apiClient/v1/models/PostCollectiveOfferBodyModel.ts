/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AddressBodyModel } from './AddressBodyModel';
import type { CollectiveLocationType } from './CollectiveLocationType';
import type { CollectiveOfferVenueBodyModel } from './CollectiveOfferVenueBodyModel';
import type { EacFormat } from './EacFormat';
import type { StudentLevels } from './StudentLevels';
export type PostCollectiveOfferBodyModel = {
  address?: AddressBodyModel | null;
  audioDisabilityCompliant?: boolean;
  bookingEmails: Array<string>;
  contactEmail?: string | null;
  contactPhone?: string | null;
  description: string;
  domains: Array<number>;
  durationMinutes?: number | null;
  formats?: Array<EacFormat> | null;
  interventionArea?: Array<string> | null;
  locationComment?: string | null;
  locationType?: CollectiveLocationType | null;
  mentalDisabilityCompliant?: boolean;
  motorDisabilityCompliant?: boolean;
  name: string;
  nationalProgramId?: number | null;
  offerVenue?: CollectiveOfferVenueBodyModel | null;
  offererId?: string | null;
  students: Array<StudentLevels>;
  subcategoryId?: string | null;
  templateId?: number | null;
  venueId: number;
  visualDisabilityCompliant?: boolean;
};


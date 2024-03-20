/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EacFormat } from './EacFormat';
import type { OfferVenueModel } from './OfferVenueModel';
export type PostCollectiveOfferBodyModel = {
  audioDisabilityCompliant?: boolean;
  beginningDatetime: string;
  bookingEmails: Array<string>;
  bookingLimitDatetime: string;
  contactEmail: string;
  contactPhone: string;
  description: string;
  domains: Array<number>;
  durationMinutes?: number | null;
  educationalInstitution?: string | null;
  educationalInstitutionId?: number | null;
  educationalPriceDetail?: string | null;
  formats?: Array<EacFormat> | null;
  imageCredit?: string | null;
  imageFile?: string | null;
  isActive: boolean;
  mentalDisabilityCompliant?: boolean;
  motorDisabilityCompliant?: boolean;
  name: string;
  nationalProgramId?: number | null;
  numberOfTickets: number;
  offerVenue: OfferVenueModel;
  students: Array<string>;
  subcategoryId?: string | null;
  totalPrice: number;
  venueId: number;
  visualDisabilityCompliant?: boolean;
};


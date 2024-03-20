/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveBookingResponseModel } from './CollectiveBookingResponseModel';
import type { EacFormat } from './EacFormat';
import type { NationalProgramModel } from './NationalProgramModel';
import type { OfferVenueModel } from './OfferVenueModel';
export type GetPublicCollectiveOfferResponseModel = {
  audioDisabilityCompliant?: boolean | null;
  beginningDatetime: string;
  bookingEmails?: Array<string> | null;
  bookingLimitDatetime: string;
  bookings: Array<CollectiveBookingResponseModel>;
  contactEmail: string;
  contactPhone: string;
  dateCreated: string;
  description?: string | null;
  domains: Array<number>;
  durationMinutes?: number | null;
  educationalInstitution?: string | null;
  educationalInstitutionId?: number | null;
  educationalPriceDetail?: string | null;
  formats?: Array<EacFormat> | null;
  hasBookingLimitDatetimesPassed: boolean;
  id: number;
  imageCredit?: string | null;
  imageUrl?: string | null;
  interventionArea: Array<string>;
  isActive?: boolean | null;
  isSoldOut: boolean;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  nationalProgram?: NationalProgramModel | null;
  numberOfTickets: number;
  offerVenue: OfferVenueModel;
  status: string;
  students: Array<string>;
  subcategoryId?: string | null;
  totalPrice: number;
  venueId: number;
  visualDisabilityCompliant?: boolean | null;
};


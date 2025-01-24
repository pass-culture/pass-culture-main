/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OfferStatus } from './OfferStatus';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';
export type GetActiveEANOfferResponseModel = {
  audioDisabilityCompliant?: boolean | null;
  dateCreated: string;
  id: number;
  isActive: boolean;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  productId?: number | null;
  status: OfferStatus;
  subcategoryId: SubcategoryIdEnum;
  visualDisabilityCompliant?: boolean | null;
};


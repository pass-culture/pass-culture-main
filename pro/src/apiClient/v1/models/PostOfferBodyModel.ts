/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AddressBodyModel } from './AddressBodyModel'
import type { WithdrawalTypeEnum } from './WithdrawalTypeEnum'
export type PostOfferBodyModel = {
  address?: AddressBodyModel | null
  audioDisabilityCompliant?: boolean | null
  bookingContact?: string | null
  bookingEmail?: string | null
  description?: string | null
  durationMinutes?: number | null
  externalTicketOfficeUrl?: string | null
  extraData?: Record<string, any> | null
  isDuo?: boolean | null
  isNational?: boolean | null
  mentalDisabilityCompliant?: boolean | null
  motorDisabilityCompliant?: boolean | null
  name: string
  subcategoryId: string
  url?: string | null
  venueId: number
  visualDisabilityCompliant?: boolean | null
  withdrawalDelay?: number | null
  withdrawalDetails?: string | null
  withdrawalType?: WithdrawalTypeEnum | null
}

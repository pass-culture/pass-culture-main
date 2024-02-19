import type { FormikProps } from 'formik'

import { WithdrawalTypeEnum } from 'apiClient/v1'
import { AccessibiltyFormValues } from 'core/shared'

export interface IndividualOfferFormValues {
  isEvent?: boolean
  subCategoryFields: string[]
  name: string
  description: string
  offererId: string
  venueId: string
  isNational: boolean
  categoryId: string
  subcategoryId: string
  showType: string
  showSubType: string
  withdrawalDetails: string
  musicType?: string
  musicSubType?: string
  gtl_id?: string
  withdrawalDelay?: number | null
  withdrawalType?: WithdrawalTypeEnum | null
  accessibility: AccessibiltyFormValues
  author?: string
  performer?: string
  ean?: string
  speaker?: string
  stageDirector?: string
  visa?: string
  durationMinutes?: string | null
  receiveNotificationEmails: boolean
  bookingEmail: string
  isDuo: boolean
  externalTicketOfficeUrl: string
  url: string
  isVenueVirtual?: boolean
  bookingContact?: string
}

export type IndividualOfferForm = FormikProps<IndividualOfferFormValues>

import type { ObjectSchema } from 'yup'

import { MAX_PRICE_DETAILS_LENGTH } from '@/commons/core/OfferEducational/constants'
import { emailSchema } from '@/commons/utils/isValidEmail'
import { yup } from '@/commons/utils/yup'
import { phoneNumberSchema } from '@/commons/utils/yup/phoneNumberSchema'

export interface CollectiveOfferInformationFormValues {
  bookingEmails?: { email: string }[]
  contactEmail?: string | null
  contactPhone?: string | null
  additionalDetails?: string
}

export const validationSchema: ObjectSchema<CollectiveOfferInformationFormValues> =
  yup.object().shape({
    bookingEmails: yup.array().of(
      yup.object().shape({
        email: yup
          .string()
          .required('Veuillez renseigner une adresse email')
          .test(emailSchema),
      })
    ),
    contactPhone: phoneNumberSchema(),
    contactEmail: yup
      .string()
      .required('Veuillez renseigner une adresse email')
      .test(emailSchema),
    additionalDetails: yup.string().max(MAX_PRICE_DETAILS_LENGTH),
  })

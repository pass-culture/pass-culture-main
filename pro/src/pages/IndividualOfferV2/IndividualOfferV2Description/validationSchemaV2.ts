import type { z } from 'zod'

import { FieldEnum } from '@/apiClient/v1'
import { zPatchOfferBodyModel } from '@/apiClient/zod/zod.gen'

const MANDATORY_FIELD_ERRORS: Partial<
  Record<FieldEnum, { path: string[]; message: string }>
> = {
  [FieldEnum.TITLE]: {
    path: ['name'],
    message: 'Veuillez renseigner un titre',
  },
  [FieldEnum.DESCRIPTION]: {
    path: ['description'],
    message: 'Veuillez renseigner une description',
  },
  [FieldEnum.GENRE_MUSIC]: {
    path: ['extraData', 'gtl_id'],
    message: 'Veuillez sélectionner un genre musical',
  },
  [FieldEnum.EAN]: {
    path: ['extraData', 'ean'],
    message: "L'EAN doit être composé de 13 chiffres.",
  },
}

const getValueAtPath = (values: unknown, path: string[]): unknown =>
  path.reduce<unknown>(
    (current, key) => (current as Record<string, unknown> | null)?.[key],
    values
  )

const isEmpty = (value: unknown) =>
  value === undefined ||
  value === null ||
  (typeof value === 'string' && value.trim() === '')

export const getValidationSchema = (mandatoryFields: string[] = []) => {
  return zPatchOfferBodyModel.superRefine((values, ctx) => {
    for (const field of mandatoryFields) {
      const fieldError = MANDATORY_FIELD_ERRORS[field as FieldEnum]
      if (fieldError && isEmpty(getValueAtPath(values, fieldError.path))) {
        ctx.addIssue({ code: 'custom', ...fieldError })
      }
    }
  })
}

export type DescriptionFormInputValues = z.input<
  ReturnType<typeof getValidationSchema>
>
export type DescriptionFormValues = z.infer<
  ReturnType<typeof getValidationSchema>
>

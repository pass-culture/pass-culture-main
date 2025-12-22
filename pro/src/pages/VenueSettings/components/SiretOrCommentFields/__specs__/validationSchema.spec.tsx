import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { yup } from '@/commons/utils/yup'
import type { VenueSettingsFormValuesType } from '@/pages/VenueSettings/commons/validationSchema'

import type { VenueSettingsFormContext } from '../../../commons/types'
import { SiretOrCommentValidationSchema } from '../validationSchema'

type SiretOrCommentFormValues = Pick<
  VenueSettingsFormValuesType,
  'siret' | 'comment'
>

describe('SiretOrCommentValidationSchema', () => {
  const baseContext: VenueSettingsFormContext = {
    isCaledonian: false,
    withSiret: true,
    siren: '123456789',
    isVenueVirtual: false,
    isVenueActivityFeatureActive: false,
  }

  const baseFormValues: SiretOrCommentFormValues = {
    siret: '12345678901234',
    comment: '',
  }

  interface Case {
    description: string
    formValues: SiretOrCommentFormValues
    context: VenueSettingsFormContext
    expectedErrors: string[]
  }

  const cases: Case[] = [
    {
      description: 'valid siret',
      formValues: baseFormValues,
      context: baseContext,
      expectedErrors: [],
    },
    {
      description: 'siret errors with no siren matching',
      formValues: {
        ...baseFormValues,
        siret: '22345678901234',
      },
      context: {
        ...baseContext,
      },
      expectedErrors: [
        'Le code SIRET doit correspondre à un établissement de votre structure',
      ],
    },
    {
      description: 'siret errors with invalid length',
      formValues: {
        ...baseFormValues,
        siret: '123457',
      },
      context: baseContext,
      expectedErrors: [
        'Le SIRET doit comporter 14 caractères',
        'Le code SIRET doit correspondre à un établissement de votre structure',
      ],
    },
    {
      description: 'siret errors with required',
      formValues: {
        ...baseFormValues,
        siret: '',
      },
      context: {
        ...baseContext,
      },
      expectedErrors: [
        'Veuillez renseigner un SIRET',
        'Le SIRET doit comporter 14 caractères',
        'Le code SIRET doit correspondre à un établissement de votre structure',
      ],
    },
    {
      description: 'valid ridet',
      formValues: {
        ...baseFormValues,
        siret: 'NC0123456789',
      },
      context: {
        ...baseContext,
        siren: 'NC0123456',
        isCaledonian: true,
      },
      expectedErrors: [],
    },
    {
      description: 'ridet errors with invalid length',
      formValues: {
        ...baseFormValues,
        siret: 'NC012345678',
      },
      context: {
        ...baseContext,
        siren: 'NC0123456',
        isCaledonian: true,
      },
      expectedErrors: ['Le RIDET doit comporter 10 caractères'],
    },
    {
      description: 'ridet errors with no rid7 matching',
      formValues: {
        ...baseFormValues,
        siret: 'NC1123456789',
      },
      context: {
        ...baseContext,
        siren: 'NC0123456',
        isCaledonian: true,
      },
      expectedErrors: [
        'Le code RIDET doit correspondre à un établissement de votre structure',
      ],
    },
    {
      description: 'valid comment',
      formValues: {
        ...baseFormValues,
        comment: 'best comment ever',
      },
      context: {
        ...baseContext,
        isVenueVirtual: true,
      },
      expectedErrors: [],
    },
    {
      description: 'comment error with required',
      formValues: {
        ...baseFormValues,
        comment: '',
      },
      context: {
        ...baseContext,
        isVenueVirtual: true,
      },
      expectedErrors: ['Veuillez renseigner un commentaire'],
    },
  ]

  cases.forEach(({ description, formValues, context, expectedErrors }) => {
    it(`should validate the form for case: ${description}`, async () => {
      const collected: string[] = []
      try {
        await SiretOrCommentValidationSchema.validate(formValues, {
          abortEarly: false,
          context: {
            ...context,
          },
        })
      } catch (error) {
        assertOrFrontendError(
          error instanceof yup.ValidationError,
          'Expected yup.ValidationError'
        )

        collected.push(...error.errors)
      }

      expect(collected).toEqual(expectedErrors)
    })
  })
})

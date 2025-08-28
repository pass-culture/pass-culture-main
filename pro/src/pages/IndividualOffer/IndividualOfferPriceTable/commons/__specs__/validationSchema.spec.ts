import * as yup from 'yup'

import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import {
  type PriceTableFormValues,
  PriceTableValidationSchema,
} from '../schemas'
import type { PriceTableFormContext } from '../types'

// Helper to build context + run validation similarly to other schema spec patterns
const buildContext = (
  overrides: Partial<PriceTableFormContext> = {}
): PriceTableFormContext => {
  const offer = getIndividualOfferFactory({
    isEvent: overrides.offer?.isEvent ?? true,
  })
  return {
    isCaledonian: false,
    mode: OFFER_WIZARD_MODE.CREATION,
    offer,
    ...overrides,
  }
}

describe('PriceTableValidationSchema', () => {
  const baseContext = buildContext()
  const baseEntry = {
    activationCodes: [],
    activationCodesExpirationDatetime: '',
    bookingLimitDatetime: '',
    bookingsQuantity: undefined,
    id: undefined,
    label: 'Normal',
    price: 10,
    quantity: 5,
    offerId: baseContext.offer.id,
    remainingQuantity: null,
  }
  const baseFormValues: PriceTableFormValues = {
    entries: [baseEntry],
    isDuo: true,
  } as unknown as PriceTableFormValues

  interface Case {
    description: string
    formValues: PriceTableFormValues
    context: PriceTableFormContext
    expectedErrors: string[]
  }

  const cases: Case[] = [
    {
      description: 'valid event form (creation)',
      formValues: baseFormValues,
      context: baseContext,
      expectedErrors: [],
    },
    {
      description:
        'missing label for event offer triggers label required error',
      formValues: {
        ...baseFormValues,
        entries: [{ ...baseEntry, label: '' }],
      },
      context: baseContext,
      expectedErrors: ['Veuillez renseigner un intitulé de tarif'],
    },
    {
      description: 'duplicate labels produce uniqueness error',
      formValues: {
        ...baseFormValues,
        entries: [baseEntry, { ...baseEntry, offerId: baseEntry.offerId }],
      },
      context: baseContext,
      expectedErrors: [
        'Plusieurs tarifs sont identiques, veuillez changer l’intitulé ou le prix',
      ],
    },
    {
      description: 'price missing for creation triggers price required error',
      formValues: {
        ...baseFormValues,
        entries: [{ ...baseEntry, price: undefined as unknown as number }],
      },
      context: baseContext,
      expectedErrors: ['Veuillez renseigner un prix'],
    },
    {
      description: 'quantity below 1 in creation triggers min error',
      formValues: {
        ...baseFormValues,
        entries: [{ ...baseEntry, quantity: 0 }],
      },
      context: baseContext,
      expectedErrors: ['Veuillez indiquer un nombre supérieur à 0'],
    },
    {
      description: 'quantity above max triggers max error',
      formValues: {
        ...baseFormValues,
        entries: [{ ...baseEntry, quantity: 1_000_000 + 1 }],
      },
      context: baseContext,
      expectedErrors: [
        'Veuillez modifier la quantité. Celle-ci ne peut pas être supérieure à 1 million',
      ],
    },
    {
      description: 'non-event offer does not require label',
      formValues: {
        ...baseFormValues,
        entries: [{ ...baseEntry, label: '' }],
      },
      context: buildContext({
        offer: getIndividualOfferFactory({ isEvent: false }),
      }),
      expectedErrors: [],
    },
    {
      description:
        'EDITION mode with existing id allows zero quantity when bookingsQuantity = 0',
      formValues: {
        ...baseFormValues,
        entries: [{ ...baseEntry, id: 42, quantity: 0 }],
      },
      context: buildContext({ mode: OFFER_WIZARD_MODE.EDITION }),
      expectedErrors: [],
    },
  ]

  cases.forEach(({ description, formValues, context, expectedErrors }) => {
    it(`should validate that ${description}`, async () => {
      const schema = PriceTableValidationSchema
      const collected: string[] = []
      try {
        await schema.validate(formValues, {
          abortEarly: false,
          context: {
            ...context,
            isCaledonian: context.isCaledonian,
            mode: context.mode,
            offer: context.offer,
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

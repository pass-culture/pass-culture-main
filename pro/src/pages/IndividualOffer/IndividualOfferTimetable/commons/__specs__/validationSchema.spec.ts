import { getYupValidationSchemaErrors } from '@/commons/utils/yupValidationTestHelpers'

import { HasDateEnum, type IndividualOfferTimetableFormValues } from '../types'
import { validationSchema } from '../validationSchema'

const baseValidForm: IndividualOfferTimetableFormValues = {
  hasEndDate: HasDateEnum.NO,
  hasStartDate: HasDateEnum.NO,
  startDate: null,
  endDate: null,
  quantityPerPriceCategories: [],
}

describe('validationSchema', () => {
  const cases: {
    description: string
    formValues: IndividualOfferTimetableFormValues
    expectedErrors: string[]
  }[] = [
    {
      description: 'valid form for the calendar type',
      formValues: baseValidForm,
      expectedErrors: [],
    },
  ]

  cases.forEach(({ description, formValues, expectedErrors }) => {
    it(`should validate the form for case: ${description}`, async () => {
      const errors = await getYupValidationSchemaErrors(
        validationSchema,
        formValues
      )
      expect(errors).toEqual(expectedErrors)
    })
  })
})

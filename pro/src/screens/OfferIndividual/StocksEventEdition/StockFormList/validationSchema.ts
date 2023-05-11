import * as yup from 'yup'

import { oneOfSelectOption } from 'core/shared/utils/validation'
import { SelectOption } from 'custom_types/form'
import { getToday, removeTime } from 'utils/date'

const isBeforeBeginningDate = (
  bookingLimitDatetime: Date | undefined | null,
  context: yup.TestContext
) => {
  if (
    !context.parent.beginningDate ||
    !bookingLimitDatetime ||
    context.parent.readOnlyFields.includes('beginningDate')
  ) {
    return true
  }
  return bookingLimitDatetime <= context.parent.beginningDate
}

const getSingleValidationSchema = (
  priceCategoriesOptions?: SelectOption[]
) => ({
  beginningDate: yup
    .date()
    .nullable()
    // A date field getting an empty string throws an error even if field is nullable or not required.
    // https://github.com/jquense/yup/issues/764
    .typeError('Veuillez renseigner une date')
    .required('Veuillez renseigner une date')
    .when(['readOnlyFields'], ([readOnlyFields], schema) => {
      /* istanbul ignore next: DEBT, TO FIX */
      if (readOnlyFields.includes('beginningDate')) {
        return schema
      }
      return schema.min(removeTime(getToday()), 'L’évènement doit être à venir')
    }),
  beginningTime: yup
    .string()
    .nullable()
    .required('Veuillez renseigner un horaire'),
  priceCategoryId: oneOfSelectOption(
    yup.string().required('Veuillez renseigner un tarif'),
    priceCategoriesOptions ?? []
  ),
  bookingLimitDatetime: yup.date().nullable().test({
    name: 'bookingLimitDatetime-before-beginningDate',
    message: 'Veuillez renseigner une date antérieure à la date de l’évènement',
    test: isBeforeBeginningDate,
  }),
  bookingsQuantity: yup.number(),
  remainingQuantity: yup
    .number()
    .nullable()
    .typeError('Doit être un nombre')
    .min(0, 'Doit être positif'),
})

export const getValidationSchema = (priceCategoriesOptions?: SelectOption[]) =>
  yup.object().shape({
    stocks: yup
      .array()
      .of(
        yup.object().shape(getSingleValidationSchema(priceCategoriesOptions))
      ),
  })

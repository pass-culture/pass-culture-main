import { format, isBefore, isEqual, isValid } from 'date-fns'
import * as yup from 'yup'
import { ObjectSchema } from 'yup'

import { oneOfSelectOption } from 'commons/core/shared/utils/validation'
import { SelectOption } from 'commons/custom_types/form'
import { FORMAT_ISO_DATE_ONLY, getToday, removeTime } from 'commons/utils/date'
import {
  StockEventFormValues,
  StocksEventFormValues,
} from 'components/IndividualOffer/StocksEventEdition/StockFormList/types'
import { MAX_STOCKS_QUANTITY } from 'components/IndividualOffer/StocksThing/validationSchema'

const isBeforeBeginningDate = (
  bookingLimitDatetime: string | undefined | null,
  context: yup.TestContext
) => {
  if (
    !context.parent.beginningDate ||
    !bookingLimitDatetime ||
    context.parent.readOnlyFields.includes('beginningDate')
  ) {
    return true
  }

  return (
    isBefore(
      new Date(bookingLimitDatetime),
      new Date(context.parent.beginningDate)
    ) ||
    isEqual(
      new Date(context.parent.beginningDate),
      new Date(bookingLimitDatetime)
    )
  )
}

const getSingleValidationSchema = (
  priceCategoriesOptions?: SelectOption[]
): ObjectSchema<StockEventFormValues> => {
  return yup.object().shape({
    beginningDate: yup
      .string()
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
        return schema
          .test((v) => (v ? isValid(new Date(v)) : true))
          .test(
            'beginningDate-before-today',
            'L’évènement doit être à venir',
            (d: string) => {
              return isBefore(removeTime(getToday()), new Date(d))
            }
          )
      })
      .transform((d) => format(d, FORMAT_ISO_DATE_ONLY)),
    beginningTime: yup
      .string()
      .nullable()
      .required('Veuillez renseigner un horaire'),
    priceCategoryId: oneOfSelectOption(
      yup.string().required('Veuillez renseigner un tarif'),
      priceCategoriesOptions ?? []
    ).required(),
    bookingLimitDatetime: yup
      .string()
      .required()
      .test(
        'bookingLimitDatetime-before-beginningDate',
        'Veuillez renseigner une date antérieure à la date de l’évènement',
        isBeforeBeginningDate
      ),
    bookingsQuantity: yup.number().required(),
    remainingQuantity: yup
      .number()
      .required()
      .typeError('Doit être un nombre')
      .min(0, 'Doit être positif')
      .max(
        MAX_STOCKS_QUANTITY,
        'Veuillez modifier la quantité. Celle-ci ne peut pas être supérieure à 1 million'
      ),
    stockId: yup.number().required(),
    isDeletable: yup.boolean().required(),
    readOnlyFields: yup.array().required(),
  })
}

export const getValidationSchema = (
  priceCategoriesOptions?: SelectOption[]
): ObjectSchema<StocksEventFormValues> =>
  yup.object().shape({
    stocks: yup
      .array()
      .required()
      .of(getSingleValidationSchema(priceCategoriesOptions)),
  })

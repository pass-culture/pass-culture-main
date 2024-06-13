import { addYears } from 'date-fns'
import * as yup from 'yup'

import { isDateValid } from 'utils/date'

export const validationSchema = yup.object().shape({
  publicationDate: yup.string().when('publicationMode', {
    is: (publicationMode: string) => publicationMode === 'later',
    then: (schema) =>
      schema
        .required('Veuillez sélectionner une date de publication')
        .test(
          'is-in-future',
          'Veuillez indiquer une date dans le futur',
          function (value) {
            return isDateValid(value) && new Date(value) > new Date()
          }
        )
        .test(
          'is-within-two-years',
          'Veuillez indiquer une date dans les 2 ans à venir',
          function (value) {
            const twoYearsFromNow = addYears(new Date(), 2)

            return isDateValid(value) && new Date(value) < twoYearsFromNow
          }
        ),
  }),
  publicationTime: yup.string().when('publicationMode', {
    is: (publicationMode: string) => publicationMode === 'later',
    then: (schema) =>
      schema.required('Veuillez sélectionner une heure de publication'),
  }),
})

import type { InferType } from 'yup'
import * as yup from 'yup'

export const validationSchema = yup.object().shape({
  educationalInstitution: yup
    .string()
    .required('Veuillez sélectionner un établissement scolaire dans la liste'),
  teacherEmail: yup.string(),
  teacherName: yup.string(),
})

export type InstitutionFormValues = InferType<typeof validationSchema>

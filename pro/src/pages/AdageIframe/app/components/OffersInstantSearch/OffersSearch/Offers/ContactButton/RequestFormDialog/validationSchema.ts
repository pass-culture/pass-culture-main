import * as yup from 'yup'

import { isPhoneValid } from 'commons/core/shared/utils/validation'

export const validationSchema = () =>
  yup.object().shape({
    teacherEmail: yup
      .string()
      .max(120)
      .email('Veuillez renseigner un email valide, exemple : mail@exemple.com')
      .required('Veuillez renseigner une adresse email'),
    teacherPhone: yup.string().test({
      name: 'is-phone-valid',
      message: 'Veuillez entrer un numéro de téléphone valide',
      test: (phone) => isPhoneValid({ phone, emptyAllowed: true }),
    }),
    offerDate: yup.date().nullable(),
    nbStudents: yup.number().nullable().min(0, 'Nombre positif attendu'),
    nbTeachers: yup.number().nullable().min(0, 'Nombre positif attendu'),
    description: yup
      .string()
      .nullable()
      .max(1000)
      .required('Veuillez préciser votre demande'),
  })

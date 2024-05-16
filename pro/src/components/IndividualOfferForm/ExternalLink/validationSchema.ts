import * as yup from 'yup'

export const validationSchema = {
  externalTicketOfficeUrl: yup
    .string()
    .url('Veuillez renseigner une URL valide. Ex : https://exemple.com'),
}

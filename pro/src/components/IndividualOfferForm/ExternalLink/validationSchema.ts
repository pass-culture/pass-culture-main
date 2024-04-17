import * as yup from 'yup'

const validationSchema = {
  externalTicketOfficeUrl: yup
    .string()
    .url('Veuillez renseigner une URL valide. Ex : https://exemple.com'),
}

export default validationSchema

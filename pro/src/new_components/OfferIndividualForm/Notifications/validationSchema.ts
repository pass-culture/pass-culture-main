import * as yup from 'yup'

const validationSchema = {
  bookingEmail: yup.string().when('receiveNotificationEmails', {
    is: (receiveNotificationEmails: boolean) => receiveNotificationEmails,
    then: yup
      .string()
      .required('Veuillez renseigner une adresse e-mail')
      .email('Veuillez renseigner un e-mail valide'),
  }),
}

export default validationSchema

import * as yup from 'yup'

const validationSchema = {
  bookingEmail: yup.string().when('receiveNotificationEmails', {
    is: (receiveNotificationEmails: boolean) => receiveNotificationEmails,
    then: yup
      .string()
      .required('Veuillez renseigner une adresse email')
      .email('Veuillez renseigner un email valide'),
  }),
}

export default validationSchema

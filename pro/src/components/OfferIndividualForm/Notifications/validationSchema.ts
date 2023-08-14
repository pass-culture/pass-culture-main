import * as yup from 'yup'

const validationSchema = {
  bookingEmail: yup.string().when('receiveNotificationEmails', {
    is: (receiveNotificationEmails: boolean) => receiveNotificationEmails,
    then: schema =>
      schema
        .required('Veuillez renseigner une adresse email')
        .email('Veuillez renseigner un email valide, exemple : mail@exemple.com'),
  }),
}

export default validationSchema

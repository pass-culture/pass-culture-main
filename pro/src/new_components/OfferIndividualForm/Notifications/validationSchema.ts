import * as yup from 'yup'

const validationSchema = {
  bookingEmail: yup.string().when('receiveNotificationEmails', {
    is: (receiveNotificationEmails: boolean) => receiveNotificationEmails,
    then: yup
      .string()
      .required('Veuillez renseigner une adresse e-mail')
      .email(
        'L’e-mail renseigné n’est pas valide. Exemple : votrenom@votremail.com'
      ),
  }),
}

export default validationSchema

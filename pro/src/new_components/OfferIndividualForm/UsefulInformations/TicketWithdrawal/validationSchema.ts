import * as yup from 'yup'
import { TICKETWITHDRAWAL } from './constants'

const validationSchema = {
  ticketWithdrawal: yup.string().when('isEvent', {
    is: (isEvent: string) => isEvent,
    then: yup
      .string()
      .required('Vous devez cocher l’une des options ci-dessus'),
    otherwise: yup.string(),
  }),
  ticketSentDate: yup.string().when('ticketWithdrawal', {
    is: (ticketWithdrawal: string) =>
      ticketWithdrawal === TICKETWITHDRAWAL.emailTicket,
    then: yup.string().required('Vous devez choisir une date d’envoi'),
    otherwise: yup.string(),
  }),
  ticketWithdrawalHour: yup.string().when('ticketWithdrawal', {
    is: (ticketWithdrawal: string) =>
      ticketWithdrawal === TICKETWITHDRAWAL.onPlaceTicket,
    then: yup.string().required('Vous devez choisir une heure de retrait'),
    otherwise: yup.string(),
  }),
}

export default validationSchema

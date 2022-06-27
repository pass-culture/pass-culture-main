import * as yup from 'yup'
import { WITHDRAWAL_TYPE } from './constants'

const validationSchema = {
  withdrawalType: yup.string().when('isEvent', {
    is: (isEvent: string) => isEvent,
    then: yup
      .string()
      .required('Vous devez cocher l’une des options ci-dessus'),
    otherwise: yup.string(),
  }),
  withdrawalDelay: yup.string().when('withdrawalType', {
    is: (withdrawalType: string) =>
      withdrawalType === WITHDRAWAL_TYPE.emailTicket ||
      withdrawalType === WITHDRAWAL_TYPE.onPlaceTicket,
    then: yup
      .string()
      .required('Vous devez choisir l’une des options ci-dessus'),
    otherwise: yup.string(),
  }),
}

export default validationSchema

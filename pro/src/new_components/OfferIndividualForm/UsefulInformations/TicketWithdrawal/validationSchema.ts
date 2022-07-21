import * as yup from 'yup'

import { WithdrawalTypeEnum } from 'apiClient/v1'

const validationSchema = {
  withdrawalType: yup.string().when('isEvent', {
    is: (isEvent: string) => isEvent,
    then: yup
      .string()
      .oneOf(
        Object.values(WithdrawalTypeEnum),
        'Vous devez cocher l’une des options ci-dessuss'
      )
      .required('Vous devez cocher l’une des options ci-dessus'),
    otherwise: yup.string(),
  }),
  withdrawalDelay: yup.string().when('withdrawalType', {
    is: (withdrawalType: string) =>
      withdrawalType === WithdrawalTypeEnum.BY_EMAIL ||
      withdrawalType === WithdrawalTypeEnum.ON_SITE,
    then: yup
      .string()
      .required('Vous devez choisir l’une des options ci-dessus'),
    otherwise: yup.string(),
  }),
}

export default validationSchema

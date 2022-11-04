import * as yup from 'yup'

import { WithdrawalTypeEnum } from 'apiClient/v1'

const validationSchema = {
  withdrawalType: yup.string().when('subCategoryFields', {
    is: (subCategoryFields: string[]) =>
      subCategoryFields.includes('withdrawalType'),
    then: yup
      .string()
      .oneOf(
        Object.values(WithdrawalTypeEnum),
        'Vous devez cocher l’une des options ci-dessuss'
      )
      .required('Vous devez cocher l’une des options ci-dessus'),
    otherwise: yup.string(),
  }),
  withdrawalDelay: yup.string().when(['subCategoryFields', 'withdrawalType'], {
    is: (subCategoryFields: string[], withdrawalType: WithdrawalTypeEnum) =>
      subCategoryFields.includes('withdrawalDelay') &&
      [WithdrawalTypeEnum.BY_EMAIL, WithdrawalTypeEnum.ON_SITE].includes(
        withdrawalType
      ),
    then: yup
      .string()
      .required('Vous devez choisir l’une des options ci-dessus'),
    otherwise: yup.string(),
  }),
}

export default validationSchema

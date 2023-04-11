import * as yup from 'yup'

import { WithdrawalTypeEnum } from 'apiClient/v1'

const validationSchema = {
  withdrawalType: yup.string().when('subCategoryFields', {
    is: (subCategoryFields: string[]) =>
      subCategoryFields.includes('withdrawalType'),
    then: schema =>
      schema
        .oneOf(Object.values(WithdrawalTypeEnum))
        .required('Veuillez sélectionner l’une de ces options'),
  }),
  withdrawalDelay: yup.string().when(['subCategoryFields', 'withdrawalType'], {
    is: (subCategoryFields: string[], withdrawalType: WithdrawalTypeEnum) =>
      subCategoryFields.includes('withdrawalDelay') &&
      [WithdrawalTypeEnum.BY_EMAIL, WithdrawalTypeEnum.ON_SITE].includes(
        withdrawalType
      ),
    then: schema =>
      schema.required('Vous devez choisir l’une des options ci-dessus'),
  }),
}

export default validationSchema

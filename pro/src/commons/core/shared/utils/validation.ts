import { StringSchema } from 'yup'

import { SelectOption } from 'commons/custom_types/form'

export const oneOfSelectOption = (
  field: StringSchema,
  options: SelectOption[]
) =>
  field.oneOf(
    options.map(({ value }) => String(value)).concat(['']),
    ({ value }) => `"${String(value)} " n’est pas une valeur valide de la liste`
  )

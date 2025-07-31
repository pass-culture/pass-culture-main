import { StringSchema } from 'yup'

import { SelectOption } from 'commons/custom_types/form'

export const oneOfSelectOption = <T extends number | string>(
  field: StringSchema,
  options: SelectOption<T>[]
) =>
  field.oneOf(
    options.map(({ value }) => String(value)).concat(['']),
    ({ value }) => `"${String(value)} " n’est pas une valeur valide de la liste`
  )

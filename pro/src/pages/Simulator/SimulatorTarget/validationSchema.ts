import * as yup from 'yup'

export const validationSchema = yup.object().shape({
  targetCustomer: yup
    .object()
    .test({
      name: 'is-one-true',
      message: 'Veuillez sélectionner au moins une option',
      test: (values: Record<string, boolean>): boolean =>
        Object.values(values).includes(true),
    })
    .shape({
      individual: yup.boolean(),
      educational: yup.boolean(),
    })
    .required('Veuillez sélectionner au moins une option'),
})

export type SimulatorTargetCustomerFormValues = yup.InferType<
  typeof validationSchema
>

import { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import SelectAutocomplete from './SelectAutocomplete'
import type { SelectAutocompleteProps } from './SelectAutocomplete'

export default {
  title: 'ui-kit/forms/SelectAutocomplete',
  component: SelectAutocomplete,
}
interface Args extends SelectAutocompleteProps {
  initialValues: { departement: string }
}

const validationSchema = yup.object().shape({
  departement: yup.string().required('Veuillez renseigner un département'),
  'search-departement': yup
    .string()
    .when('departement', (departement, schema) =>
      schema.test({
        name: 'search-departement-invalid',
        message: 'error',
        test: departement !== '' ? () => false : () => true,
      })
    ),
})

const Template: Story<Args> = args => (
  <Formik
    initialValues={args.initialValues}
    onSubmit={() => {}}
    validationSchema={validationSchema}
  >
    <SelectAutocomplete {...args} />
  </Formik>
)

const defaultProps: Args = {
  label: 'Département',
  fieldName: 'departement',
  options: [
    { value: '01', label: 'Ain' },
    { value: '02', label: 'Aisne' },
    { value: '03', label: 'Allier' },
    {
      value: '04',
      label: 'Alpes-de-Haute-Provence test de libellé très long',
    },
    { value: '05', label: 'Hautes-Alpes' },
    { value: '06', label: 'Alpes-Maritimes' },
    { value: '07', label: 'Ardèche' },
    { value: '08', label: 'Ardennes' },
    { value: '09', label: 'Ariège' },
    { value: '10', label: 'Aube' },
    { value: '11', label: 'Aude' },
    { value: '12', label: 'Aveyron' },
    { value: '13', label: 'Bouches-du-Rhône' },
    { value: '14', label: 'Calvados' },
    { value: '15', label: 'Cantal' },
  ],
  initialValues: { departement: '' },
  hideFooter: false,
  isOptional: false,
  smallLabel: false,
  disabled: false,
  filterLabel: undefined,
}

export const Default = Template.bind({})
Default.args = defaultProps

export const WithMaxDisplayOptions = Template.bind({})
WithMaxDisplayOptions.args = {
  ...defaultProps,
  maxDisplayOptions: 2,
}

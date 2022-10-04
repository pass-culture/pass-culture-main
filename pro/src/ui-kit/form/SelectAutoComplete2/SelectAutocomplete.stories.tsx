import { Formik } from 'formik'
import React from 'react'
import SelectAutocomplete from './SelectAutocomplete'
import type { SelectAutocompleteProps } from './SelectAutocomplete'
import type { Story } from '@storybook/react'

export default {
  title: 'ui-kit/forms/SelectAutocomplete2',
  component: SelectAutocomplete,
}
interface Args extends SelectAutocompleteProps {
  initialValues: { departement: string[] }
}

const Template: Story<Args> = args => (
  <Formik initialValues={args.initialValues} onSubmit={() => {}}>
    <SelectAutocomplete {...args} />
  </Formik>
)

const defaultProps: Args = {
  pluralLabel: 'Départements',
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
  initialValues: { departement: ['01', '02'] },
  label: 'Département',
  hideFooter: false,
  hideTags: false,
  isOptional: false,
  smallLabel: false,
}

export const Default = Template.bind({})
Default.args = defaultProps

export const WithoutTags = Template.bind({})
WithoutTags.args = { ...defaultProps, hideTags: true }

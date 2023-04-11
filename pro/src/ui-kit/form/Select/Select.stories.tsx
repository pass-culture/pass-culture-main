import { action } from '@storybook/addon-actions'
import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import Select, { SelectProps } from './Select'
import SelectInput, { SelectInputProps } from './SelectInput'

export default {
  title: 'ui-kit/forms/Select',
  component: Select,
}

const mockCategoriesOptions = [
  { value: 'cinema', label: 'Cinéma' },
  { value: 'theatre', label: 'Théatre' },
  { value: 'musique', label: 'Musique' },
]

const Template: Story<SelectProps> = props => (
  <Formik initialValues={{ category: 'theatre' }} onSubmit={action('onSubmit')}>
    {({ getFieldProps }) => {
      return <Select {...getFieldProps('category')} {...props} />
    }}
  </Formik>
)

export const FormikField = Template.bind({})
FormikField.args = {
  label: 'Catégorie',
  options: mockCategoriesOptions,
  disabled: false,
}

export const SelectInline = Template.bind({})
SelectInline.args = {
  label: 'Catégorie',
  options: mockCategoriesOptions,
  description: 'super select inline',
}

export const SelectFilter = Template.bind({})
SelectFilter.args = {
  options: mockCategoriesOptions,
  filterVariant: true,
}

const SelectInputTemplate: Story<SelectInputProps> = props => (
  <SelectInput {...props} />
)

export const StandeloneSelect = SelectInputTemplate.bind({})
StandeloneSelect.args = {
  name: 'select',
  hasError: false,
  options: mockCategoriesOptions,
  disabled: false,
  value: '',
}

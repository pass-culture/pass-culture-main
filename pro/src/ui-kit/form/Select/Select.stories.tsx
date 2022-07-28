import { action } from '@storybook/addon-actions'
import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import Select from './Select'
import SelectInput from './SelectInput'

export default {
  title: 'ui-kit/forms/Select',
  component: Select,
}

const mockCategoriesOptions = [
  { value: 'cinema', label: 'Cinéma' },
  { value: 'theatre', label: 'Théatre' },
  { value: 'musique', label: 'Musique' },
]

type SelectArgs = {
  label: string
  options: {
    value: string
    label: string
  }[]
  disabled: boolean
}

const Template: Story<SelectArgs> = args => (
  <Formik initialValues={{ category: 'theatre' }} onSubmit={action('onSubmit')}>
    {({ getFieldProps }) => {
      return <Select {...getFieldProps('category')} {...args} />
    }}
  </Formik>
)

export const FormikField = Template.bind({})

FormikField.args = {
  label: 'Catégorie',
  options: mockCategoriesOptions,
  disabled: false,
}

type SelectInputArgs = {
  name: string
  hasError: boolean
  options: {
    value: string
    label: string
  }[]
  disabled: boolean
  value: string
}

const SelectInputTemplate: Story<SelectInputArgs> = args => (
  <SelectInput {...args} />
)

export const StandeloneSelect = SelectInputTemplate.bind({})

StandeloneSelect.args = {
  name: 'select',
  hasError: false,
  options: mockCategoriesOptions,
  disabled: false,
  value: '',
}

type SelectInlineArgs = {
  label: string
  options: {
    value: string
    label: string
  }[]
  description: string
}

const SelectInlineTemplate: Story<SelectInlineArgs> = args => (
  <Formik
    initialValues={{ category: 'theatre' }}
    onSubmit={action('onSubmit')}
    errors={{
      category: 'Oups, même joueur joue encore.',
    }}
  >
    {({ getFieldProps }) => {
      return <Select {...getFieldProps('category')} {...args} />
    }}
  </Formik>
)

export const SelectInline = SelectInlineTemplate.bind({})
SelectInline.args = {
  label: 'Catégorie',
  options: mockCategoriesOptions,
  description: 'super select inline',
}

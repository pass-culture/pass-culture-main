import { action } from '@storybook/addon-actions'
import { Story } from "@storybook/react"
import { Formik } from 'formik'
import React from 'react'

import Select from './Select'

export default {
  title: 'ui-kit/Select',
  component: Select,
}

const mockCategoriesOptions = [
  { value: 'cinema', label: 'Cinéma' },
  { value: 'theatre', label: 'Théatre' },
  { value: 'musique', label: 'Musique' }
]

const Template: Story<{ label?: string }> = ({ label }) => (
  <Formik
    initialValues={{ categorie: 'theatre' }}
    onSubmit={action('onSubmit')}
  >
    {({ getFieldProps }) => {
      return (
        <Select
          {...getFieldProps('categorie')}
          label={label}
          options={mockCategoriesOptions}
        />
      )}}
  </Formik>
)

export const WithoutLabel = Template.bind({})
export const WithLabel = Template.bind({})
WithLabel.args = { label: 'Catégorie' }
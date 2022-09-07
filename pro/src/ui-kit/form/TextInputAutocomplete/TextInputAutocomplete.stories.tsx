import { action } from '@storybook/addon-actions'
import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import TextInputAutocomplete from './TextInputAutocomplete'

export default {
  title: 'ui-kit/forms/TextInputAutocomplete',
  component: TextInputAutocomplete,
}
const getSuggestions = () => {
  return [
    { value: '1', label: '12 rue des étoiles - 75000 - Paris' },
    { value: '2', label: '19 rue de la république - 69000 - Lyon' },
    { value: '3', label: '43 rue des fleurs - 13000 - Marseille' },
  ]
}

const validationSchema = yup.object().shape({
  adress: yup.string().required('Veuillez renseigner une adresse'),
})

const Template: Story<{ label: string }> = ({ label }) => (
  <Formik
    initialValues={{ adress: '', 'search-adress': '' }}
    onSubmit={action('onSubmit')}
    validationSchema={validationSchema}
  >
    <TextInputAutocomplete
      getSuggestions={getSuggestions}
      label={label}
      fieldName="adress"
      placeholder="input placeholder"
    />
  </Formik>
)

export const WithoutLabel = Template.bind({})
export const WithLabel = Template.bind({})
WithLabel.args = { label: 'Adresse' }

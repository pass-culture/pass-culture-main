import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import strokeSearch from 'icons/stroke-search.svg'

import TextInput, { TextInputProps } from './TextInput'

export default {
  title: 'ui-kit/forms/TextInput',
  component: TextInput,
}

const Template: Story<TextInputProps> = (props) => (
  <Formik initialValues={{ email: '' }} onSubmit={() => {}}>
    {({ getFieldProps }) => (
      <TextInput
        {...getFieldProps('email')}
        placeholder="input placeholder"
        {...props}
      />
    )}
  </Formik>
)

export const WithoutLabel = Template.bind({})
export const WithLabel = Template.bind({})
WithLabel.args = { label: 'Email' }
export const WithLeftIcon = Template.bind({})
WithLeftIcon.args = { leftIcon: strokeSearch }

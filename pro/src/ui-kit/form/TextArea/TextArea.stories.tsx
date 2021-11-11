import { action } from '@storybook/addon-actions'
import { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import TextArea from './TextArea'

export default {
  title: 'ui-kit/TextArea',
  component: TextArea,
}

const Template: Story<{label?: string}> = ({ label }) => (
  <Formik
    initialValues={{ description: '' }}
    onSubmit={action('onSubmit')}
  >
    {({ getFieldProps }) => {
      return (
        <TextArea
          {...getFieldProps('description')}
          label={label}
        />
      )}}
  </Formik>
)

export const WithoutLabel = Template.bind({})
export const WithLabel = Template.bind({})
WithLabel.args = { label: 'Description' }

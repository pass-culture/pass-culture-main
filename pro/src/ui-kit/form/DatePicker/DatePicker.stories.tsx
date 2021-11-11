import { action } from '@storybook/addon-actions'
import { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import DatePicker from './DatePicker'

export default {
  title: 'ui-kit/DatePicker',
  component: DatePicker,
}

const Template: Story<{label?: string}> = ({ label }) => (
  <Formik
    initialValues={{ date: new Date().toISOString().split('T')[0] }}
    onSubmit={action('onSubmit')}
  >
    {({ getFieldProps }) => {
      return (
        <DatePicker
          {...getFieldProps('date')}
          label={label}
          name='date'
        />
      )}}
  </Formik>
)

export const WithoutLabel = Template.bind({})
export const WithLabel = Template.bind({})
WithLabel.args = { label: 'Date' }
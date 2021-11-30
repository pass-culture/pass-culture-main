import { action } from '@storybook/addon-actions'
import { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import DatePicker from './DatePicker'

export default {
  title: 'ui-kit/forms/DatePicker',
  component: DatePicker,
}

const Template: Story<{ label?: string }> = ({ label }) => (
  <Formik initialValues={{ date: new Date() }} onSubmit={action('onSubmit')}>
    {({ getFieldProps }) => {
      return <DatePicker {...getFieldProps('date')} label={label} name="date" />
    }}
  </Formik>
)

export const WithoutLabel = Template.bind({})
export const WithLabel = Template.bind({})
WithLabel.args = { label: 'Date' }

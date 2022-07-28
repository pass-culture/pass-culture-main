import { action } from '@storybook/addon-actions'
import { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import DatePicker from './DatePicker'

export default {
  title: 'ui-kit/forms/DatePicker',
  component: DatePicker,
}

const Template: Story<{
  disabled: boolean
  smallLabel: boolean
  label: string
}> = props => (
  <Formik initialValues={{ date: '' }} onSubmit={action('onSubmit')}>
    {({ getFieldProps }) => {
      return <DatePicker {...getFieldProps('date')} {...props} />
    }}
  </Formik>
)

export const WithoutLabel = Template.bind({})
export const WithLabel = Template.bind({})
WithLabel.args = {
  disabled: false,
  label: 'label',
  smallLabel: false,
}

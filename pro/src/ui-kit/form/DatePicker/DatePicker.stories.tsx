import DatePicker from './DatePicker'
import { Formik } from 'formik'
import React from 'react'
import { Story } from '@storybook/react'
import { action } from '@storybook/addon-actions'

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

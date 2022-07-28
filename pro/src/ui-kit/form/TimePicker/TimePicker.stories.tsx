import { action } from '@storybook/addon-actions'
import { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import TimePicker from './TimePicker'

export default {
  title: 'ui-kit/forms/TimePicker',
  component: TimePicker,
}

const Template: Story<{ label: string }> = ({ label }) => (
  <Formik initialValues={{ time: '' }} onSubmit={action('onSubmit')}>
    {({ getFieldProps }) => {
      return <TimePicker {...getFieldProps('time')} label={label} name="time" />
    }}
  </Formik>
)

export const WithoutLabel = Template.bind({})
export const WithLabel = Template.bind({})

WithLabel.args = { label: 'Horaire' }

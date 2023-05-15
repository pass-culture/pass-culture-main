import { action } from '@storybook/addon-actions'
import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import DatePicker, { DatePickerProps } from './DatePicker'

export default {
  title: 'ui-kit/forms/DatePicker',
  component: DatePicker,
}

const Template: Story<DatePickerProps> = props => (
  <Formik initialValues={{ date: '' }} onSubmit={action('onSubmit')}>
    <DatePicker {...props} name="date" />
  </Formik>
)

export const WithoutLabel = Template.bind({})
export const WithLabel = Template.bind({})
WithLabel.args = {
  disabled: false,
  label: 'label',
  smallLabel: false,
}

export const FilterVariant = Template.bind({})
FilterVariant.args = {
  filterVariant: true,
}

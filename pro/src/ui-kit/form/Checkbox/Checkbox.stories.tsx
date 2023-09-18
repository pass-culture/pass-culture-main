import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import Checkbox, { CheckboxProps } from './Checkbox'

export default {
  title: 'ui-kit/forms/Checkbox',
  component: Checkbox,
}

const Template: Story<CheckboxProps> = props => (
  <Formik initialValues={{ accessibility: false }} onSubmit={() => {}}>
    {({ getFieldProps }) => {
      return <Checkbox {...getFieldProps('accessibility')} {...props} />
    }}
  </Formik>
)

export const Default = Template.bind({})

Default.args = {
  label: 'Accessible',
  name: 'accessibility',
  value: 'accessible',
}

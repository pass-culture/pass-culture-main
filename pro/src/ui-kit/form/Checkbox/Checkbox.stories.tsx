import { action } from '@storybook/addon-actions'
import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import Checkbox, { ICheckboxProps } from './Checkbox'

export default {
  title: 'ui-kit/forms/Checkbox',
  component: Checkbox,
}

const Template: Story<ICheckboxProps> = props => (
  <Formik
    initialValues={{ accessibility: false }}
    onSubmit={action('onSubmit')}
  >
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

export const WithDescription = Template.bind({})

WithDescription.args = {
  label: 'Accessible',
  description:
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
  name: 'accessibility',
  value: 'accessible',
}

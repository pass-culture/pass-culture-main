import { action } from '@storybook/addon-actions'
import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import CheckboxGroup, { ICheckboxGroupProps } from './CheckboxGroup'

export default {
  title: 'ui-kit/forms/CheckboxGroup',
  component: CheckboxGroup,
}

const Template: Story<ICheckboxGroupProps> = props => (
  <Formik
    initialValues={{ accessibility: false }}
    onSubmit={action('onSubmit')}
  >
    {({ getFieldProps }) => {
      return <CheckboxGroup {...getFieldProps('group')} {...props} />
    }}
  </Formik>
)

export const Default = Template.bind({})
Default.args = {
  group: ['foo', 'bar', 'baz'].map(item => ({
    label: item,
    name: `checkBoxes.${item}`,
  })),
  groupName: 'checkBoxes',
  legend: 'This is the legend',
}

export const WithDescription = Template.bind({})
WithDescription.args = {
  group: ['foo', 'bar', 'baz'].map(item => ({
    label: item,
    name: `checkBoxes.${item}`,
    description:
      'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
  })),
  groupName: 'checkBoxes',
  legend: 'This is the legend',
}

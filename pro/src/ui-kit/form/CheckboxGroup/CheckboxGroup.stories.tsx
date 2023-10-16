import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import CheckboxGroup, { CheckboxGroupProps } from './CheckboxGroup'

export default {
  title: 'ui-kit/forms/CheckboxGroup',
  component: CheckboxGroup,
}

const Template: Story<CheckboxGroupProps> = (props) => (
  <Formik initialValues={{ accessibility: false }} onSubmit={() => {}}>
    {({ getFieldProps }) => {
      return <CheckboxGroup {...getFieldProps('group')} {...props} />
    }}
  </Formik>
)

export const Default = Template.bind({})
Default.args = {
  group: ['foo', 'bar', 'baz'].map((item) => ({
    label: item,
    name: `checkBoxes.${item}`,
  })),
  groupName: 'checkBoxes',
  legend: 'This is the legend',
}

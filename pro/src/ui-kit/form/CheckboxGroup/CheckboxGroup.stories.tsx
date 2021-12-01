import { action } from '@storybook/addon-actions'
import { Formik } from 'formik'
import React from 'react'

import CheckboxGroup from './CheckboxGroup'

export default {
  title: 'ui-kit/forms/CheckboxGroup',
  component: CheckboxGroup,
}

const Template = () => (
  <Formik
    initialValues={{
      checkBoxes: [],
    }}
    onSubmit={action('onSubmit')}
  >
    {({ getFieldProps }) => {
      return (
        <CheckboxGroup
          {...getFieldProps('group')}
          group={['foo', 'bar', 'baz'].map(item => ({
            label: item,
            value: item,
          }))}
          name="checkBoxes"
        />
      )
    }}
  </Formik>
)

export const Default = Template.bind({})

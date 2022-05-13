import CheckboxGroup from './CheckboxGroup'
import { Formik } from 'formik'
import React from 'react'
import { action } from '@storybook/addon-actions'

export default {
  title: 'ui-kit/forms/CheckboxGroup',
  component: CheckboxGroup,
}

const Template = () => (
  <Formik
    initialValues={{
      checkBoxes: {
        foo: false,
        bar: false,
        baz: true,
      },
    }}
    onSubmit={action('onSubmit')}
  >
    {({ getFieldProps }) => {
      return (
        <CheckboxGroup
          {...getFieldProps('group')}
          group={['foo', 'bar', 'baz'].map(item => ({
            label: item,
            name: `checkBoxes.${item}`,
          }))}
          groupName="checkBoxes"
          legend="This is the legend"
        />
      )
    }}
  </Formik>
)

export const Default = Template.bind({})

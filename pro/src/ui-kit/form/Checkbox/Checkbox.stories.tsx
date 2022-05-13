import Checkbox from './Checkbox'
import { Formik } from 'formik'
import React from 'react'
import { action } from '@storybook/addon-actions'

export default {
  title: 'ui-kit/forms/Checkbox',
  component: Checkbox,
}

const Template = () => (
  <Formik
    initialValues={{ accessibility: false }}
    onSubmit={action('onSubmit')}
  >
    {({ getFieldProps }) => {
      return (
        <Checkbox
          {...getFieldProps('accessibility')}
          label="Accessible"
          name="accessibility"
          value="accessible"
        />
      )
    }}
  </Formik>
)

export const Default = Template.bind({})

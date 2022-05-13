import { Formik } from 'formik'
import RadioButton from './RadioButton'
import React from 'react'
import { action } from '@storybook/addon-actions'

export default {
  title: 'ui-kit/forms/RadioButton',
  component: RadioButton,
}

const Template = () => (
  <Formik initialValues={{}} onSubmit={action('onSubmit')}>
    {({ getFieldProps }) => {
      return (
        <>
          <RadioButton
            {...getFieldProps('gender')}
            label="Male"
            name="gender"
            value="male"
          />
          <RadioButton
            {...getFieldProps('gender')}
            label="Female"
            name="gender"
            value="female"
          />
        </>
      )
    }}
  </Formik>
)

export const Default = Template.bind({})

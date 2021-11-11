import { action } from '@storybook/addon-actions'
import { Formik } from 'formik'
import React from 'react'

import RadioButton from './RadioButton'

export default {
  title: 'ui-kit/RadioButton',
  component: RadioButton,
}

const Template = () => (
  <Formik
    initialValues={{}}
    onSubmit={action('onSubmit')}
  >
    {({ getFieldProps }) => {
      return (
        <>
          <RadioButton
            {...getFieldProps('gender')}
            label="Male"
            name='gender'
            value="male"
          /> 
          <RadioButton
            {...getFieldProps('gender')}
            label="Female"
            name='gender'
            value="female"
          />
        </>
      )}}
  </Formik>
)

export const Default = Template.bind({})

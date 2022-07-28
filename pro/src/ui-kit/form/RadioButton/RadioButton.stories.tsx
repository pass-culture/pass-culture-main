import { action } from '@storybook/addon-actions'
import { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import RadioButton from './RadioButton'

export default {
  title: 'ui-kit/forms/RadioButton',
  component: RadioButton,
}

const Template: Story<{
  withBorder?: boolean
}> = ({ withBorder }) => (
  <Formik initialValues={{}} onSubmit={action('onSubmit')}>
    {({ getFieldProps }) => {
      return (
        <>
          <RadioButton
            {...getFieldProps('gender')}
            label="Male"
            name="gender"
            value="male"
            withBorder={withBorder}
          />
          <RadioButton
            {...getFieldProps('gender')}
            label="Female"
            name="gender"
            value="female"
            withBorder={withBorder}
          />
        </>
      )
    }}
  </Formik>
)

export const Default = Template.bind({})
export const WithBorder = Template.bind({})
WithBorder.args = { withBorder: true }

import { Formik } from 'formik'
import React from 'react'
import { Story } from '@storybook/react'
import TextArea from './TextArea'
import { action } from '@storybook/addon-actions'

export default {
  title: 'ui-kit/forms/TextArea',
  component: TextArea,
}

const Template: Story<{ label: string; disabled: boolean }> = ({
  label,
  disabled,
}) => (
  <Formik initialValues={{ description: '' }} onSubmit={action('onSubmit')}>
    {({ getFieldProps }) => {
      return (
        <TextArea
          {...getFieldProps('description')}
          disabled={disabled}
          label={label}
          placeholder="Description placeholder"
        />
      )
    }}
  </Formik>
)

export const WithoutLabel = Template.bind({})
export const WithLabel = Template.bind({})
WithLabel.args = { label: 'Description', disabled: false }

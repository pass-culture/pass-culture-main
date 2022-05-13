import FieldError from './FieldError'
import React from 'react'

export default {
  title: 'ui-kit/forms/shared/FieldError',
  component: FieldError,
}

const Template = () => <FieldError name="foo"> field error message </FieldError>

export const Default = Template.bind({})

import React from 'react'

import FieldError from './FieldError'

export default {
  title: 'ui-kit/forms/shared/FieldError',
  component: FieldError,
}

const Template = () => <FieldError name="foo"> field error message </FieldError>

export const Default = Template.bind({})

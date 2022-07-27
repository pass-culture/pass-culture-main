import React from 'react'
import { Form } from 'react-final-form'

import { ReactComponent as MotorDisabilitySvg } from 'icons/motor-disability.svg'

import CheckboxField from './CheckboxField'

export default {
  title: 'ui-kit/CheckboxField',
  component: CheckboxField,
}

const submitForm = () => {
  return true
}

const Template = args => (
  <Form onSubmit={submitForm}>
    {() => (
      <div className="field-group">
        <CheckboxField {...args} />
      </div>
    )}
  </Form>
)

export const Default = Template.bind({})

Default.args = {
  id: 'test-checkbox',
  label: 'Checkbox label',
  labelAligned: true,
  name: 'test-checkbox',
}

export const WithIcon = Template.bind({})

WithIcon.args = {
  SvgElement: MotorDisabilitySvg,
  id: 'test-checkbox',
  label: 'Checkbox label',
  labelAligned: true,
  name: 'test-checkbox',
}

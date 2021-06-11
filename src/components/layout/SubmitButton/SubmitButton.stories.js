import React from 'react'

import SubmitButton from './SubmitButton'


export default {
  title: 'layout/SubmitButton',
  component: SubmitButton,
}

const Template = (args) => (
  <SubmitButton {...args} >
    {args.children}
  </SubmitButton>
)

export const Primary = Template.bind({})

Primary.args = {
  onClick: () => {},
  children: 'hello',
  isLoading: false,
  disabled: false
}

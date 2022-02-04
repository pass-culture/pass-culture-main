import React from 'react'

import SubmitButton from './SubmitButton'

export default {
  title: 'ui-kit/SubmitButton',
  component: SubmitButton,
}

const Template = args => <SubmitButton {...args}>{args.children}</SubmitButton>

export const Default = Template.bind({})

Default.args = {
  onClick: () => {},
  children: 'Envoyer',
  isLoading: false,
  disabled: false,
}

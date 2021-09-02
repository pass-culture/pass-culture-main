import React from 'react'

import Button from './Button'

export default {
  title: 'ui-kit/Button',
  component: Button,
}

const Template = args => (
  <Button {...args}>
    {args.children}
  </Button>
)

export const Default = Template.bind({})

Default.args = {
  onClick: () => {},
  children: 'Envoyer',
  disabled: false,
  type: 'button'
}

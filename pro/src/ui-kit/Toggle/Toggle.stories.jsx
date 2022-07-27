import React from 'react'

import Toggle from './Toggle'

export default {
  title: 'ui-kit/Toggle',
  component: Toggle,
}

const Template = args => <Toggle {...args} />

export const Default = Template.bind({})

Default.args = {
  isActiveByDefault: false,
  isDisabled: false,
}

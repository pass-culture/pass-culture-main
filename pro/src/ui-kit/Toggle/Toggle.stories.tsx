import type { Story } from '@storybook/react'
import React from 'react'

import Toggle, { ToggleProps } from './Toggle'

export default {
  title: 'ui-kit/Toggle',
  component: Toggle,
}

const Template: Story<ToggleProps> = args => <Toggle {...args} />

export const Default = Template.bind({})
Default.args = {
  isActiveByDefault: false,
  isDisabled: false,
}

import type { Story } from '@storybook/react'
import React from 'react'

import DialogBox, { DialogProps } from './DialogBox'

export default {
  title: 'components/DialogBox',
  component: DialogBox,
}
const Template: Story<DialogProps> = args => (
  <DialogBox {...args}>
    <p>lorem ipsum dolor sit amet</p>
  </DialogBox>
)

export const Default = Template.bind({})

Default.args = {
  extraClassNames: 'extraClassNames',
  hasCloseButton: false,
  labelledBy: 'labelledBy',
  onDismiss: undefined,
}

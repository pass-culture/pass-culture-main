import React from 'react'

import DialogBox from './DialogBox'

export default {
  title: 'components/DialogBox',
  component: DialogBox,
}
const Template = args => (
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
  initialFocusRef: null,
}

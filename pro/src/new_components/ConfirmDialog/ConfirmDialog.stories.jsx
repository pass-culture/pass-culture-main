import React from 'react'

import ConfirmDialog from './ConfirmDialog'

export default {
  title: 'components/ConfirmDialog',
  component: ConfirmDialog,
}
const Template = args => (
  <ConfirmDialog {...args}>
    <p>lorem ipsum dolor sit amet</p>
  </ConfirmDialog>
)

export const Default = Template.bind({})

Default.args = {
  onConfirm: () => {},
  onCancel: () => {},
  title: 'title',
  confirmText: 'confirmText',
  cancelText: 'cancelText',
}

import { ComponentMeta, ComponentStory } from '@storybook/react'
import React from 'react'

import ConfirmDialog from './ConfirmDialog'

export default {
  title: 'components/ConfirmDialog',
  component: ConfirmDialog,
} as ComponentMeta<typeof ConfirmDialog>

const Template: ComponentStory<typeof ConfirmDialog> = args => (
  <ConfirmDialog {...args}>
    <p>lorem ipsum dolor sit amet</p>
  </ConfirmDialog>
)

export const Default = Template.bind({})
Default.args = {
  title: 'title',
  confirmText: 'confirmText',
  cancelText: 'cancelText',
}

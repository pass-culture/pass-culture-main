import type { ComponentMeta, ComponentStory } from '@storybook/react'
import React from 'react'

import { ReactComponent as TrashIcon } from 'icons/ico-trash.svg'

import ConfirmDialog from './ConfirmDialog'

export default {
  title: 'components/ConfirmDialog',
  component: ConfirmDialog,
} as ComponentMeta<typeof ConfirmDialog>

const Template: ComponentStory<typeof ConfirmDialog> = args => (
  <ConfirmDialog {...args} />
)

export const Default = Template.bind({})
Default.args = {
  title: 'title',
  confirmText: 'confirm',
  cancelText: 'cancel',
  children: 'lorem ipsum dolor sit amet',
}

export const WithLoading = Template.bind({})
WithLoading.args = {
  title: 'title',
  confirmText: 'confirm',
  cancelText: 'cancel',
  children: 'lorem ipsum dolor sit amet',
  isLoading: true,
}

export const WithIcon = Template.bind({})
WithIcon.args = {
  title: 'title',
  confirmText: 'confirm',
  cancelText: 'cancel',
  children: 'lorem ipsum dolor sit amet',
  icon: TrashIcon,
}

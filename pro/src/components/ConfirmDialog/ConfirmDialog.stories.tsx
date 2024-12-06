import type { StoryObj } from '@storybook/react'

import strokeTrashIcon from 'icons/stroke-trash.svg'

import { ConfirmDialog } from './ConfirmDialog'

export default {
  title: 'components/Dialog/ConfirmDialog',
  component: ConfirmDialog,
}

export const Default: StoryObj<typeof ConfirmDialog> = {
  args: {
    title: 'title',
    confirmText: 'confirm',
    cancelText: 'cancel',
    children: 'lorem ipsum dolor sit amet',
  },
}

export const WithLoading: StoryObj<typeof ConfirmDialog> = {
  args: {
    title: 'title',
    confirmText: 'confirm',
    cancelText: 'cancel',
    children: 'lorem ipsum dolor sit amet',
    isLoading: true,
  },
}

export const WithIcon: StoryObj<typeof ConfirmDialog> = {
  args: {
    title: 'title',
    confirmText: 'confirm',
    cancelText: 'cancel',
    children: 'lorem ipsum dolor sit amet',
    icon: strokeTrashIcon,
  },
}

import type { StoryObj } from '@storybook/react-vite'

import strokeTrashIcon from '@/icons/stroke-trash.svg'

import { Dialog } from './Dialog'

export default {
  title: '@/components/Dialog/Dialog',
  component: Dialog,
}

export const Default: StoryObj<typeof Dialog> = {
  args: {
    title: 'title',
    children: 'lorem ipsum dolor sit amet',
    open: true,
  },
}

export const WithLoading: StoryObj<typeof Dialog> = {
  args: {
    title: 'title',
    children: 'lorem ipsum dolor sit amet',
    open: true,
  },
}

export const WithIcon: StoryObj<typeof Dialog> = {
  args: {
    title: 'title',
    children: 'lorem ipsum dolor sit amet',
    icon: strokeTrashIcon,
    open: true,
  },
}

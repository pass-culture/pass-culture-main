import * as Dialog from '@radix-ui/react-dialog'
import type { StoryObj } from '@storybook/react'

import { Button } from 'ui-kit/Button/Button'

import { DialogBuilder } from './DialogBuilder'

export default {
  title: 'ui-kit/DialogBuilder',
  component: DialogBuilder,
}

export const Default: StoryObj<typeof DialogBuilder> = {
  args: {
    trigger: <Button>Cliquez ici!</Button>,
    children: (
      <>
        <Dialog.Title asChild>
          <h1>Dialog title</h1>
        </Dialog.Title>
        <p>lorem ipsum dolor sit amet</p>
      </>
    ),
  },
}

export const Drawer: StoryObj<typeof DialogBuilder> = {
  args: {
    variant: 'drawer',
    trigger: <Button>Cliquez ici!</Button>,
    children: (
      <>
        <Dialog.Title asChild>
          <h1>Dialog title</h1>
        </Dialog.Title>
        <p>lorem ipsum dolor sit amet</p>
      </>
    ),
  },
}

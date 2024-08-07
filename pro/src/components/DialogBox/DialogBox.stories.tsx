import type { StoryObj } from '@storybook/react'
import React from 'react'

import { DialogBox } from './DialogBox'

export default {
  title: 'components/Dialog/DialogBox',
  component: DialogBox,
}

export const Default: StoryObj<typeof DialogBox> = {
  args: {
    extraClassNames: 'extraClassNames',
    hasCloseButton: false,
    labelledBy: 'labelledBy',
    onDismiss: undefined,
    children: <p>lorem ipsum dolor sit amet</p>,
  },
}

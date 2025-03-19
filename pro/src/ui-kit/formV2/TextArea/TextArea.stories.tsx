import type { Meta, StoryObj } from '@storybook/react'
import { useState } from 'react'

import { TextArea, TextAreaProps } from './TextArea'

const meta: Meta<typeof TextArea> = {
  title: 'ui-kit/formsV2/TextArea',
  component: TextArea,
}

export default meta
type Story = StoryObj<typeof TextArea>

export const Default: Story = {
  args: {
    name: 'email',
    label: 'Email',
    isLabelHidden: true,
    required: true,
  },
}

export const ReadOnly: Story = {
  args: {
    ...Default.args,
    readOnly: true,
    value: 'A text wrapped in a span',
    required: false,
  },
}

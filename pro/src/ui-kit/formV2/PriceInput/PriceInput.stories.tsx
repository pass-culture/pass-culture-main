import type { Meta, StoryObj } from '@storybook/react'

import { PriceInput } from './PriceInput'

const meta: Meta<typeof PriceInput> = {
  title: 'ui-kit/formsV2/PriceInput',
  component: PriceInput,
}

export default meta
type Story = StoryObj<typeof PriceInput>

export const Default: Story = {
  args: {
    name: 'email',
    label: 'Email',
  },
}

export const WithCheckbox: Story = {
  args: {
    name: 'email',
    label: 'Email',
    showFreeCheckbox: true,
  },
}

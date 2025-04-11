import type { Meta, StoryObj } from '@storybook/react'

import { QuantityInput } from './QuantityInput'

const meta: Meta<typeof QuantityInput> = {
  title: 'ui-kit/formsV2/QuantityInput',
  component: QuantityInput,
}

export default meta
type Story = StoryObj<typeof QuantityInput>

export const Default: Story = {
  args: {
    name: 'quantity',
    label: 'Quantité',
  },
}

export const SmallLabel: Story = {
  args: {
    name: 'quantity',
    label: 'Quantité',
    smallLabel: true,
  },
}

export const Required: Story = {
  args: {
    name: 'quantity',
    label: 'Quantité',
    required: true,
  },
}

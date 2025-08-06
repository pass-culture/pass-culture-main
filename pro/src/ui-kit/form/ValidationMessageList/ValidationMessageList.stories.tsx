import type { Meta, StoryObj } from '@storybook/react'

import { ValidationMessageList } from './ValidationMessageList'

const meta: Meta<typeof ValidationMessageList> = {
  title: '@/ui-kit/formsV2/ValidationMessageList',
  component: ValidationMessageList,
}

export default meta
type Story = StoryObj<typeof ValidationMessageList>

export const Default: Story = {
  args: {
    passwordValue: 'change me', // ggignore
    hasError: false,
  },
}

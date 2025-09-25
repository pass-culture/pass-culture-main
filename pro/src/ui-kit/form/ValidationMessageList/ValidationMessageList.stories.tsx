import type { Meta, StoryObj } from '@storybook/react-vite'

import { ValidationMessageList } from './ValidationMessageList'

const meta: Meta<typeof ValidationMessageList> = {
  title: '@/ui-kit/forms/ValidationMessageList',
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

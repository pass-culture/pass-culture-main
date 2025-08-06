import type { StoryObj } from '@storybook/react'

import strokeCalendarIcon from '@/icons/stroke-calendar.svg'

import { BaseInput } from './BaseInput'

export default {
  title: '@/ui-kit/forms/shared/BaseInput',
  component: BaseInput,
}

export const Default: StoryObj<typeof BaseInput> = {
  args: {
    hasError: false,
    rightIcon: strokeCalendarIcon,
  },
}

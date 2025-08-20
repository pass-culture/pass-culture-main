import type { StoryObj } from '@storybook/react'

import { Toggle } from './Toggle'

export default {
  title: '@/ui-kit/forms/Toggle',
  component: Toggle,
}

export const Default: StoryObj<typeof Toggle> = {
  args: {
    isActiveByDefault: false,
    isDisabled: false,
  },
}

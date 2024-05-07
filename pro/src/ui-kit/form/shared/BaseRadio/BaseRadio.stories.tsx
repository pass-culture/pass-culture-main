import type { StoryObj } from '@storybook/react'

import { BaseRadio } from './BaseRadio'

export default {
  title: 'ui-kit/forms/shared/BaseRadio',
  component: BaseRadio,
}

export const Default: StoryObj<typeof BaseRadio> = {
  args: {
    label: 'radio label',
    hasError: false,
    disabled: false,
    checked: false,
  },
}

export const WithBorder: StoryObj<typeof BaseRadio> = {
  args: {
    label: 'radio label',
    hasError: false,
    disabled: false,
    checked: false,
    withBorder: true,
  },
}

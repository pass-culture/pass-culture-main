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

export const WithChildren: StoryObj<typeof BaseRadio> = {
  args: {
    label: 'radio label',
    hasError: false,
    disabled: false,
    checked: true,
    withBorder: true,
    childrenOnChecked: (
      <div>Sub content displayed when the radio input is selected.</div>
    ),
  },
}

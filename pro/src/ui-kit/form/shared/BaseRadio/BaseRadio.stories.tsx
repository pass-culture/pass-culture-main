import type { StoryObj } from '@storybook/react'

import { Tag, TagVariant } from 'design-system/Tag/Tag'
import icon from 'icons/stroke-accessibility-brain.svg'

import { BaseRadio, RadioVariant } from './BaseRadio'

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
    variant: RadioVariant.BOX,
  },
}

export const WithChildren: StoryObj<typeof BaseRadio> = {
  args: {
    label: 'radio label',
    hasError: false,
    disabled: false,
    checked: true,
    variant: RadioVariant.BOX,
    childrenOnChecked: (
      <div>Sub content displayed when the radio input is selected.</div>
    ),
  },
}

export const WithIcon: StoryObj<typeof BaseRadio> = {
  args: {
    label: 'radio label',
    hasError: false,
    disabled: false,
    checked: true,
    variant: RadioVariant.BOX,
    icon: icon,
  },
}

export const WithCenteredIcon: StoryObj<typeof BaseRadio> = {
  args: {
    label: 'radio label',
    hasError: false,
    disabled: false,
    checked: true,
    variant: RadioVariant.BOX,
    icon: icon,
    iconPosition: 'center',
  },
}

export const WithIconAndDescription: StoryObj<typeof BaseRadio> = {
  args: {
    label: 'radio label',
    hasError: false,
    disabled: false,
    checked: true,
    variant: RadioVariant.BOX,
    icon: icon,
    description: 'Lorem ipsum...',
  },
}

export const WithCustomLabel: StoryObj<typeof BaseRadio> = {
  args: {
    label: (
      <div>
        <Tag label="Nouveau" variant={TagVariant.NEW} />
        <div style={{ marginTop: '8px' }}>radio label</div>
      </div>
    ),
    hasError: false,
    disabled: false,
    checked: true,
    variant: RadioVariant.BOX,
    description:
      'Lorem ipsum dolor sit amet. Et libero officia 33 perferendis quam ut tempore quos hic dolorum? Hic repellat nemo facilis magnam aut eaque fuga ex magnam cupiditate eos consequatur repellat. Cum enim repellendus qui omnis impedit et autem quod rem libero officiis est rerum possimus.',
  },
}

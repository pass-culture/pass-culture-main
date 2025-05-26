import type { StoryObj } from '@storybook/react'

import { TagVariant } from 'design-system/Tag/Tag'
import strokeCalendarIcon from 'icons/stroke-date.svg'

import dog from '../assets/dog.jpg'

import { Checkbox, CheckboxVariant } from './Checkbox'
import {
  CheckboxAssetImageSizeVariant,
  CheckboxAssetVariant,
} from './CheckboxAsset/CheckboxAsset'

export default {
  title: 'design-system/Checkbox',
  component: Checkbox,
  parameters: {
    controls: {
      exclude: [
        'onChange',
        'onBlur',
        'name',
        'className',
        'asset',
        'collapsed',
      ],
    },
  },
}

export const Default: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: CheckboxVariant.DEFAULT,
  },
}

export const DefaultChecked: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: CheckboxVariant.DEFAULT,
    checked: true,
  },
}

export const DefaultIndeterminate: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: CheckboxVariant.DEFAULT,
    checked: true,
    indeterminate: true,
  },
}

export const DefaultHasError: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: CheckboxVariant.DEFAULT,
    hasError: true,
  },
}

export const DefaultDisabled: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: CheckboxVariant.DEFAULT,
    disabled: true,
  },
}

export const DetailedWithDescription: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: CheckboxVariant.DETAILED,
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
  },
}

export const DetailedFill: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: CheckboxVariant.DETAILED,
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    display: 'fill',
  },
}

export const DetailedChecked: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: CheckboxVariant.DETAILED,
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    checked: true,
  },
}

export const DetailedHasError: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: CheckboxVariant.DETAILED,
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    hasError: true,
  },
}

export const DetailedDisabled: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: CheckboxVariant.DETAILED,
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    disabled: true,
  },
}

export const DetailedWithIcon: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: CheckboxVariant.DETAILED,
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    asset: { variant: CheckboxAssetVariant.ICON, src: strokeCalendarIcon },
  },
}

export const DetailedWithText: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: CheckboxVariant.DETAILED,
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    asset: { variant: CheckboxAssetVariant.TEXT, text: '32 €' },
  },
}

export const DetailedWithImage: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: CheckboxVariant.DETAILED,
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    asset: { variant: CheckboxAssetVariant.IMAGE, src: dog },
  },
}

export const DetailedWithMediumImage: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'detailed',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    asset: { variant: 'image', src: dog, size: 'm' },
  },
}

export const DetailedWithBigImage: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: CheckboxVariant.DETAILED,
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    asset: {
      variant: CheckboxAssetVariant.IMAGE,
      src: dog,
      size: CheckboxAssetImageSizeVariant.L,
    },
  },
}

export const DetailedWithTag: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: CheckboxVariant.DETAILED,
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    asset: {
      variant: 'tag',
      tag: { label: 'Tag label', variant: TagVariant.HEADLINE },
    },
  },
}

export const DetailedWithCollapsedContent: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: CheckboxVariant.DETAILED,
    asset: { variant: CheckboxAssetVariant.ICON, src: strokeCalendarIcon },
    checked: true,
    collapsed: <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>,
  },
}

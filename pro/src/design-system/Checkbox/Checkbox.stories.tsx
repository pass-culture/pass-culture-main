import type { StoryObj } from '@storybook/react-vite'

import { TagVariant } from '@/design-system/Tag/Tag'
import strokeCalendarIcon from '@/icons/stroke-date.svg'

import dog from '../assets/dog.jpg'
import { Checkbox } from './Checkbox'

export default {
  title: '@/design-system/Checkbox',
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
        'asterisk',
      ],
    },
  },
}

export const Default: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'default',
  },
}

export const DefaultChecked: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'default',
    checked: true,
  },
}

export const DefaultIndeterminate: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'default',
    checked: true,
    indeterminate: true,
  },
}

export const DefaultRequiredSymbol: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'default',
    checked: true,
    required: true,
    requiredIndicator: 'symbol'
  },
}

export const DefaultRequiredExplicit: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'default',
    checked: true,
    required: true,
    requiredIndicator: 'explicit'
  },
}

export const DefaultHasError: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'default',
    hasError: true,
  },
}

export const DefaultDisabled: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'default',
    disabled: true,
  },
}

export const DetailedWithDescription: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'detailed',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
  },
}

export const DetailedFill: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'detailed',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    sizing: 'fill',
  },
}

export const DetailedChecked: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'detailed',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    checked: true,
  },
}

export const DetailedIndeterminate: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'detailed',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    indeterminate: true,
  },
}

export const DetailedHasError: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'detailed',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    hasError: true,
  },
}

export const DetailedDisabled: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'detailed',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    disabled: true,
  },
}

export const DetailedWithIconNoDescription: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'detailed',
    asset: { variant: 'icon', src: strokeCalendarIcon },
  },
}

export const DetailedWithIcon: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'detailed',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    asset: { variant: 'icon', src: strokeCalendarIcon },
  },
}

export const DetailedWithText: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'detailed',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    asset: { variant: 'text', text: '32 €' },
  },
}

export const DetailedWithImage: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'detailed',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    asset: { variant: 'image', src: dog },
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
    variant: 'detailed',
    description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
    asset: {
      variant: 'image',
      src: dog,
      size: 'l',
    },
  },
}

export const DetailedWithTag: StoryObj<typeof Checkbox> = {
  args: {
    label: 'Checkbox label',
    variant: 'detailed',
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
    variant: 'detailed',
    asset: { variant: 'icon', src: strokeCalendarIcon },
    checked: true,
    collapsed: <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>,
  },
}

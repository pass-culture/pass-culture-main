import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { TagVariant } from '@/design-system/Tag/Tag'
import strokeDateIcon from '@/icons/stroke-date.svg'

import imageDemo from '../assets/dog.jpg'
import { RadioButton } from './RadioButton'

export default {
  title: '@/design-system/RadioButton',
  decorators: [withRouter],
  argTypes: {
    checked: {
      control: 'boolean',
    },
    disabled: {
      control: 'boolean',
    },
  },
  component: RadioButton,
}

export const Default: StoryObj<typeof RadioButton> = {
  args: {
    name: 'default',
    label: 'Label',
  },
}

export const DefaultDisabled: StoryObj<typeof RadioButton> = {
  args: {
    name: 'disabled',
    label: 'Désactivé',
    disabled: true,
  },
}

export const Detailed: StoryObj<typeof RadioButton> = {
  args: {
    name: 'detailed',
    label: 'Détaillé',
    variant: 'detailed',
  },
}

export const DetailedWithDescription: StoryObj<typeof RadioButton> = {
  args: {
    name: 'detailed-with-description',
    label: 'Avec description',
    variant: 'detailed',
    description: 'Description lorem ipsum',
  },
}

export const DetailedFullWidth: StoryObj<typeof RadioButton> = {
  args: {
    name: 'detailed-full-width',
    label: 'Taille étendue',
    variant: 'detailed',
    description: 'Description lorem ipsum',
    sizing: 'fill',
  },
}

export const DetailedWithTag: StoryObj<typeof RadioButton> = {
  args: {
    name: 'detailed-with-tag',
    label: 'Avec tag',
    variant: 'detailed',
    description: 'Description lorem ipsum',
    asset: {
      variant: 'tag',
      tag: {
        label: 'Tag',
        variant: TagVariant.SUCCESS,
      },
    },
  },
}

export const DetailedWithIcon: StoryObj<typeof RadioButton> = {
  args: {
    name: 'detailed-with-icon',
    label: 'Avec icône',
    variant: 'detailed',
    description: 'Description lorem ipsum',
    asset: {
      variant: 'icon',
      src: strokeDateIcon,
    },
  },
}

export const DetailedWithText: StoryObj<typeof RadioButton> = {
  args: {
    name: 'detailed-with-text',
    label: 'Avec texte',
    variant: 'detailed',
    description: 'Description lorem ipsum',
    asset: {
      variant: 'text',
      text: '19€',
    },
  },
}

export const DetailedWithImage: StoryObj<typeof RadioButton> = {
  args: {
    name: 'detailed-with-image',
    label: 'Avec image',
    variant: 'detailed',
    asset: {
      variant: 'image',
      src: imageDemo,
      size: 's',
    },
  },
}

export const DetailedWithCollapsed: StoryObj<typeof RadioButton> = {
  args: {
    name: 'detailed-with-collapsed',
    label: 'Avec enfants',
    variant: 'detailed',
    description: 'Description lorem ipsum',
    value: 'today',
    checked: true,
    onChange: () => {},
    collapsed: (
      <div style={{ display: 'flex', flexDirection: 'row', gap: 16 }}>
        <RadioButton name="subchoice" label="Sous-label 1" value="1" />
        <RadioButton name="subchoice" label="Sous-label 2" value="2" />
      </div>
    ),
  },
}

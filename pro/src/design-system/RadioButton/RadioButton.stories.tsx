import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { Tag, TagVariant } from 'design-system/Tag/Tag'
import strokeDateIcon from 'icons/stroke-date.svg'

import imageDemo from './assets/image-demo.png'
import { RadioButton } from './RadioButton'

export default {
  title: 'design-system/RadioButton',
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
    variant: 'DETAILED',
  },
}

export const DetailedWithDescription: StoryObj<typeof RadioButton> = {
  args: {
    name: 'detailed-with-description',
    label: 'Avec description',
    variant: 'DETAILED',
    description: 'Description lorem ipsum',
  },
}

export const DetailedFullWidth: StoryObj<typeof RadioButton> = {
  args: {
    name: 'detailed-full-width',
    label: 'Taille étendue',
    variant: 'DETAILED',
    description: 'Description lorem ipsum',
    sizing: 'FILL',
  },
}

export const DetailedWithTag: StoryObj<typeof RadioButton> = {
  args: {
    name: 'detailed-with-tag',
    label: 'Avec tag',
    variant: 'DETAILED',
    description: 'Description lorem ipsum',
    tag: <Tag variant={TagVariant.DEFAULT} label="Tag" />,
  },
}

export const DetailedWithIcon: StoryObj<typeof RadioButton> = {
  args: {
    name: 'detailed-with-icon',
    label: 'Avec icône',
    variant: 'DETAILED',
    description: 'Description lorem ipsum',
    icon: strokeDateIcon,
  },
}

export const DetailedWithText: StoryObj<typeof RadioButton> = {
  args: {
    name: 'detailed-with-text',
    label: 'Avec texte',
    variant: 'DETAILED',
    description: 'Description lorem ipsum',
    text: '19€',
  },
}

export const DetailedWithImage: StoryObj<typeof RadioButton> = {
  args: {
    name: 'detailed-with-image',
    label: 'Avec image',
    variant: 'DETAILED',
    image: imageDemo,
    imageSize: 'S',
  },
}

export const DetailedWithCollapsed: StoryObj<typeof RadioButton> = {
  args: {
    name: 'detailed-with-collapsed',
    label: 'Avec enfants',
    variant: 'DETAILED',
    description: 'Description lorem ipsum',
    value: 'today',
    checked: true,
    onChange: () => {},
    collapsed: (
      <div style={{ display: 'flex', flexDirection: 'row', gap: 16 }}>
        <RadioButton
          variant="DETAILED"
          name="subchoice"
          label="Sous-label 1"
          value="1"
        />
        <RadioButton
          variant="DETAILED"
          name="subchoice"
          label="Sous-label 2"
          value="2"
        />
      </div>
    ),
  },
}

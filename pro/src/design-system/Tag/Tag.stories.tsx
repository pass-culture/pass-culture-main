import { Meta, StoryObj } from '@storybook/react'

import icon from 'icons/full-location.svg'

import { Tag, TagVariant, TagSpecificVariant } from './Tag'

const meta: Meta<typeof Tag> = {
  title: 'design-system/Tag',
  component: Tag,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof Tag>

export const Default: Story = {
  args: {
    label: 'Default',
    variant: TagVariant.DEFAULT,
  },
}

export const Success: Story = {
  args: {
    label: 'Succès',
    variant: TagVariant.SUCCESS,
  },
}

export const Warning: Story = {
  args: {
    label: 'Alerte',
    variant: TagVariant.WARNING,
  },
}

export const Error: Story = {
  args: {
    label: 'Erreur',
    variant: TagVariant.ERROR,
  },
}

export const New: Story = {
  args: {
    label: 'Nouveau',
    variant: TagVariant.NEW,
  },
}

export const WithCustomIcon: Story = {
  args: {
    label: 'Avec une icône personnalisée',
    variant: TagVariant.DEFAULT,
    icon,
  },
}

export const Bookclub: Story = {
  args: {
    label: 'Reco du Book Club',
    variant: TagSpecificVariant.BOOKCLUB,
  },
}

export const Headline: Story = {
  args: {
    label: 'Reco par les lieux',
    variant: TagSpecificVariant.HEADLINE,
  },
}

export const Like: Story = {
  args: {
    label: 'x jaime',
    variant: TagSpecificVariant.LIKE,
  },
}

import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import strokeProfIcon from '@/icons/stroke-prof.svg'
import strokeThingIcon from '@/icons/stroke-thing.svg'

import { CardLink } from './CardLink'

export default {
  title: '@/ui-kit/CardLink',
  decorators: [withRouter],
  component: CardLink,
}

export const Default: StoryObj<typeof CardLink> = {
  args: {
    to: '/',
    label: 'Un bien physique',
    description: 'Livre, instrument de musique, abonnement, cartes et pass…',
    icon: strokeThingIcon,
  },
}

export const Vertical: StoryObj<typeof CardLink> = {
  args: {
    to: '/',
    label: 'À un groupe scolaire',
    description: 'Pour les enseignants, les élèves, les parents…',
    icon: strokeProfIcon,
    direction: 'vertical',
  },
}

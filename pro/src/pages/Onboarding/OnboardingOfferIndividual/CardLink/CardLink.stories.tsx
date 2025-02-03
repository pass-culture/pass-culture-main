import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import strokeMailIcon from 'icons/stroke-mail.svg'
import strokeProfIcon from 'icons/stroke-prof.svg'
import strokeThingIcon from 'icons/stroke-thing.svg'

import { CardLink } from './CardLink'

export default {
  title: 'ui-kit/CardLink',
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

export const Disabled: StoryObj<typeof CardLink> = {
  args: {
    to: 'https://www.google.fr', // should not be clickable
    label: 'Mairie de Meudon',
    description: '12 rue du chemin vert 92190 Meudon',
    icon: strokeMailIcon,
    direction: 'horizontal',
    disabled: true,
  },
}

export const WithError: StoryObj<typeof CardLink> = {
  args: {
    to: '/',
    label: 'Mairie de Meudon',
    description: '12 rue du chemin vert 92190 Meudon',
    icon: strokeMailIcon,
    direction: 'horizontal',
    error: 'Error lorem ipsum',
  },
}

export const WithErrorVertical: StoryObj<typeof CardLink> = {
  args: {
    to: '/',
    label: 'Mairie de Meudon',
    description: '12 rue du chemin vert 92190 Meudon',
    icon: strokeMailIcon,
    direction: 'vertical',
    error: 'Error lorem ipsum',
  },
}

import type { StoryObj } from '@storybook/react-vite'
import { withRouter } from 'storybook-addon-remix-react-router'

import { Title } from './Title'

export default {
  title: '@/ui-kit/Title',
  decorators: [withRouter],
  component: Title,
}

export const Niveau1: StoryObj<typeof Title> = {
  args: {
    level: '1',
    title: 'Bienvenue sur pass Culture pro !',
  },
}

export const Niveau2: StoryObj<typeof Title> = {
  args: {
    level: '2',
    title: 'Le portail professionnel des acteurs culturels',
  },
}

export const Niveau3: StoryObj<typeof Title> = {
  args: {
    level: '3',
    title: 'L’ensemble des outils à votre disposition',
  },
}

export const Niveau4: StoryObj<typeof Title> = {
  args: {
    level: '4',
    title: 'Des informations claires et fiables',
  },
}

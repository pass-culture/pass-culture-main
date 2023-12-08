import type { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-react-router-v6'

import fullShowIcon from 'icons/full-show.svg'
import shadowTrophyIcon from 'icons/shadow-trophy.svg'

import IconLinkBox from './IconLinkBox'

export default {
  title: 'ui-kit/StatBox',
  decorators: [withRouter],
  component: IconLinkBox,
}

export const Default: StoryObj<typeof IconLinkBox> = {
  args: {
    title: 'Répartition de votre chiffre d’affaires',
    linkTitle: 'Voir le tableau',
    linkUrl: '#',
    iconHeader: shadowTrophyIcon,
    iconLink: fullShowIcon,
  },
}

import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-react-router-v6'

import { Hero } from './Hero'

export default {
  title: 'components/Hero',
  component: Hero,
  decorators: [withRouter],
}

export const Default: StoryObj<typeof Hero> = {
  args: {
    title: 'Mon titre',
    text: 'Une petite explication',
    linkLabel: 'cliquez-moi !',
    linkTo: '/',
  },
}

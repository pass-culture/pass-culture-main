import type { StoryObj } from '@storybook/react-vite'
import { withRouter } from 'storybook-addon-remix-react-router'

import { NavLinkItems } from './NavLinkItems'

export default {
  title: '@/ui-kit/NavLinkItems',
  decorators: [withRouter],
  component: NavLinkItems,
}

export const Default: StoryObj<typeof NavLinkItems> = {
  args: {
    selectedKey: 'individual',
    links: [
      {
        label: 'Offres individuelles',
        url: '#',
        key: 'individual',
      },
      {
        label: 'Offres collectives',
        url: '#',
        key: 'collective',
      },
    ],
  },
}

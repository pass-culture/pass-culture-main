import type { StoryObj } from '@storybook/react-vite'
import { withRouter } from 'storybook-addon-remix-react-router'

import { Tabs } from './Tabs'

export default {
  title: '@/ui-kit/Tabs',
  decorators: [withRouter],
  component: Tabs,
}

export const NavLinksMode: StoryObj<typeof Tabs> = {
  args: {
    selectedKey: 'individual',
    items: [
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

export const TabMode: StoryObj<typeof Tabs> = {
  args: {
    type: 'tabs',
    selectedKey: 'tab1',
    items: [{
      key: 'tab1',
      label: 'Tab 1'
    }, {
      key: 'tab2',
      label: 'Tab 2'
    }]
  }
}



import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { Tabs } from './Tabs'

export default {
  title: 'ui-kit/Tabs',
  decorators: [withRouter],
  component: Tabs,
}

export const Default: StoryObj<typeof Tabs> = {
  args: {
    selectedKey: 'individual',
    tabs: [
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

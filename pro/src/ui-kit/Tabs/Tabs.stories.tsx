import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-react-router-v6'

import strokeLibraryIcon from 'icons/stroke-library.svg'
import strokeUserIcon from 'icons/stroke-user.svg'

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
        url: 'offres/indiv',
        key: 'individual',
        icon: strokeUserIcon,
      },
      {
        label: 'Offres collectives',
        url: 'offres/collectives',
        key: 'collective',
        icon: strokeLibraryIcon,
      },
    ],
  },
}

export const DefaultWithButton: StoryObj<typeof Tabs> = {
  args: {
    selectedKey: 'individual',
    tabs: [
      {
        label: 'Offres individuelles',
        onClick: () => {},
        key: 'individual',
        icon: strokeUserIcon,
      },
      {
        label: 'Offres collectives',
        onClick: () => {},
        key: 'collective',
        icon: strokeLibraryIcon,
      },
    ],
  },
}

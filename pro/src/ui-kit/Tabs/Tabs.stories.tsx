import type { Story } from '@storybook/react'
import React from 'react'
import { withRouter } from 'storybook-addon-react-router-v6'

import strokeLibraryIcon from 'icons/stroke-library.svg'
import strokeUserIcon from 'icons/stroke-user.svg'

import Tabs, { FilterTabsProps } from './Tabs'
export default {
  title: 'ui-kit/Tabs',
  decorators: [withRouter],
  component: Tabs,
}

const Template: Story<FilterTabsProps> = args => {
  return <Tabs {...args} />
}

export const Default = Template.bind({})

Default.args = {
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
}

import type { Story } from '@storybook/react'
import React from 'react'

import strokeLibraryIcon from 'icons/stroke-library.svg'
import strokeUserIcon from 'icons/stroke-user.svg'
import { withRouterDecorator } from 'stories/decorators/withRouter'

import Tabs, { FilterTabsProps } from './Tabs'
export default {
  title: 'ui-kit/Tabs',
  decorators: [withRouterDecorator],
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

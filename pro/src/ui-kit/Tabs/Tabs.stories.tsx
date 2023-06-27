import type { Story } from '@storybook/react'
import React from 'react'

import LibraryIcon from 'icons/library.svg'
import UserIcon from 'icons/user.svg'
import { withRouterDecorator } from 'stories/decorators/withRouter'

import Tabs, { IFilterTabsProps } from './Tabs'
export default {
  title: 'ui-kit/Tabs',
  decorators: [withRouterDecorator],
  component: Tabs,
}

const Template: Story<IFilterTabsProps> = args => {
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
      Icon: UserIcon,
    },
    {
      label: 'Offres collectives',
      url: 'offres/collectives',
      key: 'collective',
      Icon: LibraryIcon,
    },
  ],
}

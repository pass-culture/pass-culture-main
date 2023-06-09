import type { Story } from '@storybook/react'
import React from 'react'

import { ReactComponent as LibraryIcon } from 'icons/library.svg'
import { ReactComponent as strokeUserIcon } from 'icons/stroke-user.svg'
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
      Icon: strokeUserIcon,
    },
    {
      label: 'Offres collectives',
      url: 'offres/collectives',
      key: 'collective',
      Icon: LibraryIcon,
    },
  ],
}

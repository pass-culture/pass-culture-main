import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { DescriptionList } from '@/ui-kit/DescriptionList/DescriptionList'

export default {
  title: '@/ui-kit/DescriptionList',
  decorators: [withRouter],
  component: DescriptionList,
}

export const Default: StoryObj<typeof DescriptionList> = {

  args: {lines: [{label: 'key',  value: 'value'}, {label: 'key2', value: 'value2'}]},
}

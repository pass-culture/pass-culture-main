import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { DataDisplaying } from './DataDisplaying'

export default {
  title: '@/ui-kit/DataDisplaying',
  decorators: [withRouter],
  component: DataDisplaying,
}

export const Default: StoryObj<typeof DataDisplaying> = {

  args: {lines: [{label: 'key',  value: 'value'}, {label: 'key2', value: 'value2'}]},
}

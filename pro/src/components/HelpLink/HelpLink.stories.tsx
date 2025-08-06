import { withRouter } from 'storybook-addon-remix-react-router'

import { HelpLink } from './HelpLink'

export default {
  title: '@/components/HelpLink',
  component: HelpLink,
  decorators: [
    (Story: any) => (
      <div style={{ width: 500, height: 500 }}>
        <Story />
      </div>
    ),
    withRouter,
  ],
}

export const Default = {}

---
to: <%= absPath %>/<%= component_name %>.stories.tsx
skip_if: <%= includeStorie === false %>
---
// storybook doc : https://storybook.js.org/docs/react/writing-stories/introduction
import { Story, Meta } from '@storybook/react'
import React from 'react'

import { <%= component_name %> } from './'

type Props = React.ComponentProps<typeof <%= component_name %>>

const csf: Meta = {
  title: '<%= category %>/<%= component_name %>',
}

const Template: Story<Props> = args => <<%= component_name %> {...args} />

export const c1 = Template.bind({})
c1.storyName = 'default'

export default csf

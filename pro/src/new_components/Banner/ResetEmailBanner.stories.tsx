// storybook doc : https://storybook.js.org/docs/react/writing-stories/introduction
import { Meta, Story } from '@storybook/react'
import React from 'react'

import { ResetEmailBanner } from './'

type Props = React.ComponentProps<typeof ResetEmailBanner>

const csf: Meta = {
  title: 'components/ResetEmailBanner',
}

const Template: Story<Props> = args => <ResetEmailBanner {...args} />

export const c1 = Template.bind({})
c1.storyName = 'default'
c1.args = {
  email: 'email@test.com',
}

export default csf

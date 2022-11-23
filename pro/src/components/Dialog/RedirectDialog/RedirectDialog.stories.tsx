import type { ComponentMeta, ComponentStory } from '@storybook/react'
import React from 'react'

import RedirectDialog from './RedirectDialog'

export default {
  title: 'components/RedirectDialog',
  component: RedirectDialog,
} as ComponentMeta<typeof RedirectDialog>

const Template: ComponentStory<typeof RedirectDialog> = args => (
  <RedirectDialog {...args} />
)

export const Default = Template.bind({})
Default.args = {
  title: 'title',
  redirectText: 'Go to ...',
  redirectLink: {
    to: 'https://aide.passculture.app',
    isExternal: true,
  },
  cancelText: 'cancel',
  children: 'lorem ipsum dolor sit amet',
}

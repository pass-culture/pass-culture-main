import type { Story } from '@storybook/react'
import React from 'react'

import fullShowIcon from 'icons/full-show.svg'
import shadowTropheeIcon from 'icons/shadow-trophee.svg'

import { withRouterDecorator } from '../../stories/decorators/withRouter'

import IconLinkBox, { IconLinkBoxProps } from './IconLinkBox'
export default {
  title: 'ui-kit/StatBox',
  decorators: [withRouterDecorator],
  component: IconLinkBox,
}

const Template: Story<IconLinkBoxProps> = props => (
  <div style={{ width: '265px', height: '104px' }}>
    <IconLinkBox {...props} />
  </div>
)

export const Default = Template.bind({})
Default.args = {
  title: 'Répartition de votre chiffre d’affaires',
  linkTitle: 'Voir le tableau',
  linkUrl: '#',
  iconHeader: shadowTropheeIcon,
  iconLink: fullShowIcon,
}

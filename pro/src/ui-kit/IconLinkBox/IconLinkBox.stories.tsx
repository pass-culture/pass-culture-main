import type { Story } from '@storybook/react'
import React from 'react'
import { withRouter } from 'storybook-addon-react-router-v6'

import fullShowIcon from 'icons/full-show.svg'
import shadowTrophyIcon from 'icons/shadow-trophy.svg'

import IconLinkBox, { IconLinkBoxProps } from './IconLinkBox'
export default {
  title: 'ui-kit/StatBox',
  decorators: [withRouter],
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
  iconHeader: shadowTrophyIcon,
  iconLink: fullShowIcon,
}

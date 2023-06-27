import type { Story } from '@storybook/react'
import React from 'react'

import { ReactComponent as TropheeIcon } from 'icons/ico-trophee.svg'
import Icon from 'ui-kit/Icon/Icon'

import IconLinkBox, { IconLinkBoxProps } from './IconLinkBox'

export default {
  title: 'ui-kit/StatBox',
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
  IconHeader: TropheeIcon,
  IconLink: () => <Icon svg="ico-eye-open-filled-black" />,
}

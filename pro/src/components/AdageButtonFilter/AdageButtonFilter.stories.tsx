import type { Story } from '@storybook/react'
import React from 'react'

import AdageButtonFilter, { AdageButtonFilterProps } from './AdageButtonFilter'

export default {
  title: 'components/AdageButtonFilter',
  component: AdageButtonFilter,
}
const Template: Story<AdageButtonFilterProps> = props => (
  <AdageButtonFilter {...props} />
)

export const AdageButton = Template.bind({})

AdageButton.args = {
  title: 'Lieu de l’intervention',
  children: <div>lieu de l'intervention modal</div>,
  isActive: false,
  disabled: false,
}

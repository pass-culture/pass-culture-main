import type { Story } from '@storybook/react'
import React from 'react'

import demoImage from './demo-image.jpg'
import { VenueImage, VenueImageProps } from './VenueImage'

export default {
  title: 'components/VenueImage',
  component: VenueImage,
}

export const Default: Story<VenueImageProps> = props => (
  <VenueImage {...props} />
)
Default.args = {
  url: demoImage,
}

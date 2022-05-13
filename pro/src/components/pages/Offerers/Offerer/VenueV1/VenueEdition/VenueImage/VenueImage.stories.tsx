import { VenueImage, VenueImageProps } from './VenueImage'

import React from 'react'
import { Story } from '@storybook/react'
import demoImage from './demo-image.jpg'

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

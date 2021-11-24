import React from 'react'

import { withPageTemplate } from '../../stories/decorators/withPageTemplate'
import { withRouterDecorator } from '../../stories/decorators/withRouter'

import OfferEducationalConfirmation from './OfferEducationalConfirmation'

export default {
  title: 'screens/OfferEducationalConfirmation',
  component: OfferEducationalConfirmation,
  decorators: [withRouterDecorator, withPageTemplate],
}

const Template = () => <OfferEducationalConfirmation />

export const Default = Template.bind({})

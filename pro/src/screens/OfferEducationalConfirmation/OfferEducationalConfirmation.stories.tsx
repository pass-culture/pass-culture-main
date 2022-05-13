import OfferEducationalConfirmation from './OfferEducationalConfirmation'
import React from 'react'
import { withPageTemplate } from '../../stories/decorators/withPageTemplate'
import { withRouterDecorator } from '../../stories/decorators/withRouter'

export default {
  title: 'screens/OfferEducationalConfirmation',
  component: OfferEducationalConfirmation,
  decorators: [withRouterDecorator, withPageTemplate],
}

const Template = () => <OfferEducationalConfirmation offererId={null} />

export const Default = Template.bind({})

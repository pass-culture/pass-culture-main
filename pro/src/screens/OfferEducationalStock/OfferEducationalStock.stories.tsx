import { action } from '@storybook/addon-actions'
import React from 'react'

import { DEFAULT_EAC_STOCK_FORM_VALUES, Mode } from 'core/OfferEducational'
import { OfferStatus } from 'custom_types/offer'

import { withPageTemplate } from '../../stories/decorators/withPageTemplate'
import { withRouterDecorator } from '../../stories/decorators/withRouter'

import OfferEducationalStock from '.'
export default {
  title: 'screens/OfferEducationalStock',
  component: OfferEducationalStock,
  decorators: [withRouterDecorator, withPageTemplate],
}

const Template = () => (
  <OfferEducationalStock
    initialValues={DEFAULT_EAC_STOCK_FORM_VALUES}
    mode={Mode.CREATION}
    offer={{
      id: '1234',
      status: OfferStatus.OFFER_STATUS_DRAFT,
      venue: {
        departementCode: '974',
        managingOffererId: 'AB',
      },
      isActive: true,
      audioDisabilityCompliant: true,
      mentalDisabilityCompliant: true,
      motorDisabilityCompliant: true,
      visualDisabilityCompliant: true,
      name: 'Mon offre',
      subcategoryId: 'CINEMA',
      venueId: 'DA',
    }}
    onSubmit={action('onSubmit')}
  />
)

export const Default = Template.bind({})

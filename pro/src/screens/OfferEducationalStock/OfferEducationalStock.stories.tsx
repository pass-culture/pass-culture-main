import { action } from '@storybook/addon-actions'
import React from 'react'

import { withPageTemplate } from '../../stories/decorators/withPageTemplate'
import { withRouterDecorator } from '../../stories/decorators/withRouter'

import { OfferStatus } from './constants/offerStatus'

import OfferEducationalStock from '.'
export default {
  title: 'screens/OfferEducationalStock',
  component: OfferEducationalStock,
  decorators: [withRouterDecorator, withPageTemplate],
}

const Template = () => (
  <OfferEducationalStock
    initialValues={{
      eventDate: '',
      eventTime: '',
      numberOfPlaces: '',
      totalPrice: '',
      bookingLimitDatetime: '',
    }}
    offer={{
      id: '1234',
      status: OfferStatus.OFFER_STATUS_DRAFT,
      venue: {
        departementCode: '974',
      },
    }}
    onSubmit={action('onSubmit')}
  />
)

export const Default = Template.bind({})

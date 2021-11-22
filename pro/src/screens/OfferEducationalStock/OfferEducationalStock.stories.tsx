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
      eventDate: new Date(),
      eventTime: '',
      numberOfPlaces: '',
      totalPrice: '',
      bookingLimitDatetime: new Date(),
    }}
    offer={{
      id: '1234',
      status: OfferStatus.OFFER_STATUS_DRAFT,
    }}
    onSubmit={action('onSubmit')}
  />
)

export const Default = Template.bind({})

import { Story } from '@storybook/react'
import React from 'react'

import { DEFAULT_EAC_STOCK_FORM_VALUES, Mode } from 'core/OfferEducational'
import { OfferStatus } from 'custom_types/offer'

import { withPageTemplate } from '../../stories/decorators/withPageTemplate'
import { withRouterDecorator } from '../../stories/decorators/withRouter'

import OfferEducationalStock from '.'
export default {
  title: 'screens/OfferEducationalStock',
  component: OfferEducationalStock,
  argTypes: {
    mode: {
      options: [Mode.CREATION, Mode.EDITION, Mode.READ_ONLY],
      control: { type: 'radio' },
    },
  },
  decorators: [withRouterDecorator, withPageTemplate],
}

const Template: Story<{ mode: Mode }> = args => (
  <OfferEducationalStock
    cancelActiveBookings={() => null}
    initialValues={DEFAULT_EAC_STOCK_FORM_VALUES}
    offer={{
      id: '1234',
      status: OfferStatus.OFFER_STATUS_DRAFT,
      venueDepartmentCode: '974',
      isActive: true,
      isBooked: true,
      managingOffererId: 'AA',
      isEducational: true,
      isShowcase: false,
    }}
    onSubmit={jest.fn()}
    setIsOfferActive={() => null}
    {...args}
  />
)

export const Default = Template.bind({})

Default.args = {
  mode: Mode.READ_ONLY,
}

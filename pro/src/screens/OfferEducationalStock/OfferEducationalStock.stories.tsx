import { DEFAULT_EAC_STOCK_FORM_VALUES, Mode } from 'core/OfferEducational'

import OfferEducationalStock from '.'
import { OfferStatus } from 'api/v1/gen'
import React from 'react'
import { Story } from '@storybook/react'
import { withPageTemplate } from '../../stories/decorators/withPageTemplate'
import { withRouterDecorator } from '../../stories/decorators/withRouter'

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
      status: OfferStatus.DRAFT,
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

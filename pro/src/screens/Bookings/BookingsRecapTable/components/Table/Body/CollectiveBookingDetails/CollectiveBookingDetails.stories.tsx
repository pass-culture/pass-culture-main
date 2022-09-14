import type { Story } from '@storybook/react'
import React from 'react'

import { OfferAddressType, StudentLevels } from 'apiClient/v1'

import CollectiveBookingDetails, {
  ICollectiveBookingDetailsProps,
} from './CollectiveBookingDetails'

export default {
  title:
    'screens/Bookings/BookingsRecapTable/components/CollectiveBookingDetails',
}

const Template: Story<ICollectiveBookingDetailsProps> = args => (
  <CollectiveBookingDetails {...args} />
)

export const Default = Template.bind({})
Default.args = {
  bookingDetails: {
    id: 1,
    beginningDatetime: new Date('2022-01-23T10:30:00').toISOString(),
    venuePostalCode: '75017',
    offerVenue: {
      addressType: OfferAddressType.OFFERER_VENUE,
      otherAddress: '',
      venueId: 'V1',
    },
    numberOfTickets: 10,
    price: 0,
    students: [StudentLevels.COLL_GE_4E],
    educationalInstitution: {
      institutionType: 'LYCEE PROFESIONNEL',
      name: 'Métier Alexandre Bérard',
      postalCode: '01500',
      city: 'Ambérieu-en-Buguey',
      id: 1,
      phoneNumber: '0672930477',
    },
    educationalRedactor: {
      firstName: 'Benoit',
      lastName: 'Demon',
      email: 'benoit.demon@lyc-alexandreberard.com',
      civility: 'M',
      id: 1,
    },
  },
}

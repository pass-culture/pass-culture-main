import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { renderWithProviders } from 'utils/renderWithProviders'

import VenueItem from '../VenueItem'

const mockLogEvent = jest.fn()

const renderItem = () => {
  const props = {
    venue: {
      id: 'AAA',
      managingOffererId: 'ABC',
      name: 'fake name',
      publicName: null,
    },
  }

  return renderWithProviders(<VenueItem {...props} />)
}

describe('venue Item offer link', () => {
  it('should track when clicking on offer creation page', async () => {
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    renderItem()
    await userEvent.click(screen.queryByText('Créer une offre'))

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'Offerer',
        isEdition: false,
        to: 'OfferFormHomepage',
        used: 'OffererLink',
      }
    )
  })
})

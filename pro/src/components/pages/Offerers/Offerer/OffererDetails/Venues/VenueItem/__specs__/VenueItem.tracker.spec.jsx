import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as useAnalytics from 'components/hooks/useAnalytics'
import { Events } from 'core/FirebaseEvents/constants'
import { configureTestStore } from 'store/testUtils'

import VenueItem from '../VenueItem'

const mockLogEvent = jest.fn()

const renderItem = () => {
  const store = configureTestStore({})
  const props = {
    venue: {
      id: 'AAA',
      managingOffererId: 'ABC',
      name: 'fake name',
      publicName: null,
    },
  }

  return render(
    <Provider store={store}>
      <MemoryRouter>
        <VenueItem {...props} />
      </MemoryRouter>
    </Provider>
  )
}

describe('venue Item offer link', () => {
  it('should track when clicking on offer creation page', async () => {
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
    renderItem()
    await userEvent.click(await screen.queryByText('Créer une offre'))

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

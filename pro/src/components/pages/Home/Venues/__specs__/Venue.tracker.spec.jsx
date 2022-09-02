import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as useAnalytics from 'components/hooks/useAnalytics'
import Venue from 'components/pages/Home/Venues/Venue'
import { Events } from 'core/FirebaseEvents/constants'
import { configureTestStore } from 'store/testUtils'
import { loadFakeApiVenueStats } from 'utils/fakeApi'

const mockLogEvent = jest.fn()

const renderVenue = async props => {
  const store = configureTestStore()
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <Venue {...props} />
      </MemoryRouter>
    </Provider>
  )
}

describe('venue create offer link', () => {
  let props

  beforeEach(() => {
    props = {
      id: 'VENUE01',
      isVirtual: false,
      name: 'My venue',
      offererId: 'OFFERER01',
    }
    loadFakeApiVenueStats({
      activeBookingsQuantity: 0,
      activeOffersCount: 2,
      soldOutOffersCount: 3,
      validatedBookingsQuantity: 1,
    })
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should track with virtual param', async () => {
    // Given
    props.isVirtual = true

    // When
    await renderVenue(props)
    await userEvent.click(screen.getByTitle('Afficher'))
    await userEvent.click(
      screen.getByRole('link', { name: 'Créer une nouvelle offre numérique' })
    )

    // Then
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'Home',
        isEdition: false,
        to: 'OfferFormHomepage',
        used: 'HomeVirtualLink',
      }
    )
  })

  it('should track with physical param', async () => {
    // Given
    props.isVirtual = false

    // When
    await renderVenue(props)
    await userEvent.click(screen.getByTitle('Afficher'))
    await userEvent.click(
      screen.getByRole('link', { name: 'Créer une nouvelle offre' })
    )

    // Then
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'Home',
        isEdition: false,
        to: 'OfferFormHomepage',
        used: 'HomeLink',
      }
    )
  })
})

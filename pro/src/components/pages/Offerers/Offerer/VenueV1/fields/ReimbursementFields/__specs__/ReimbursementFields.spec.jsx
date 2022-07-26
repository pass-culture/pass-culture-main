import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'

import { Form } from 'react-final-form'
import { Provider } from 'react-redux'
import React from 'react'
import ReimbursementFields from '../ReimbursementFields'
import { api } from 'apiClient/api'
import { configureTestStore } from 'store/testUtils'

const renderReimbursementFields = async (props, store) => {
  const rtlReturn = await render(
    <Provider store={store}>
      <Form onSubmit={() => {}}>
        {() => <ReimbursementFields {...props} />}
      </Form>
    </Provider>
  )

  const loadingMessage = screen.queryByText('Chargement en cours ...')
  await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

  return rtlReturn
}

jest.mock('apiClient/api', () => ({
  api: {
    getAvailableReimbursementPoints: jest.fn(),
  },
}))

describe('src | Venue | ReimbursementFields', () => {
  const venue = {
    id: 'AA',
    nonHumanizedId: 1,
    name: 'fake venue name',
  }
  const otherVenue = {
    id: 'CC',
    nonHumanizedId: 2,
    name: 'Offerer Venue',
  }
  const offerer = {
    id: 'BB',
    nonHumanizedId: 2,
    name: 'fake offerer name',
    managedVenues: [otherVenue],
    hasAvailablePricingPoints: true,
  }
  const mockLogEvent = jest.fn()
  let props
  let store
  beforeEach(() => {
    props = { venue, offerer }
    store = configureTestStore({
      app: { logEvent: mockLogEvent },
    })
    jest.spyOn(api, 'getAvailableReimbursementPoints').mockResolvedValue([])
  })

  it('should display banner if offerer has no pricing point and venue has no siret', async () => {
    // Given
    const offererWithoutPricingPoint = {
      ...offerer,
      hasAvailablePricingPoints: false,
    }
    props.offerer = offererWithoutPricingPoint

    // When
    await renderReimbursementFields(props, store)

    // Then
    expect(screen.queryByText('Créer un lieu avec SIRET')).toBeInTheDocument()
  })

  it('should not display pricing point section venue has siret', async () => {
    // Given
    const venueWithSiret = {
      ...venue,
      siret: '00000000012345',
    }
    props.venue = venueWithSiret

    // When
    await renderReimbursementFields(props, store)

    // Then
    expect(
      screen.queryByText('Barème de remboursement')
    ).not.toBeInTheDocument()
  })

  it('should display pricing point section when venue has no siret', async () => {
    // Given
    const venueWithoutSiret = {
      ...venue,
      siret: null,
    }
    props.venue = venueWithoutSiret

    // When
    await renderReimbursementFields(props, store)

    // Then
    expect(screen.queryByText('Barème de remboursement')).toBeInTheDocument()
  })
})

import '@testing-library/jest-dom'

import { act, render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { api } from 'apiClient/api'
import { configureTestStore } from 'store/testUtils'

import OffererDetails from '../OffererDetails'

jest.mock('repository/pcapi/pcapi', () => ({
  getBusinessUnits: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  api: {
    getOfferer: jest.fn(),
  },
}))

const renderOffererDetails = async ({ props, store }) => {
  return await act(async () => {
    await render(
      <Provider store={store}>
        <MemoryRouter>
          <OffererDetails {...props} />
        </MemoryRouter>
      </Provider>
    )
  })
}

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    offererId: 'AA',
  }),
}))

describe('src | components | pages | Offerer | OffererDetails', () => {
  let props
  let store
  beforeEach(() => {
    store = configureTestStore()
  })

  api.getOfferer.mockResolvedValue({
    id: 'AA',
    name: 'fake offerer name',
    address: 'fake address',
    bic: 'ABC',
    iban: 'DEF',
    managedVenues: [
      {
        address: '1 fake address',
        name: 'fake venue',
        publicName: 'fake venue',
        postalCode: '75000',
        city: 'Paris',
      },
    ],
  })

  describe('render', () => {
    it('should render Venues', async () => {
      // when
      await renderOffererDetails({ props, store })

      // then
      expect(screen.getByText('Lieux')).toBeInTheDocument()
      expect(screen.getByText('fake venue')).toBeInTheDocument()
    })
  })
})

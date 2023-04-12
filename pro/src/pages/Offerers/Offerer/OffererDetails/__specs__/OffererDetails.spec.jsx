import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { renderWithProviders } from 'utils/renderWithProviders'

import OffererDetails from '../OffererDetails'

jest.mock('apiClient/api', () => ({
  api: {
    getOfferer: jest.fn(),
  },
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    offererId: 'AA',
  }),
}))

describe('src | components | pages | Offerer | OffererDetails', () => {
  let props
  const offererId = 1

  api.getOfferer.mockResolvedValue({
    id: 'AA',
    nonHumanizedId: offererId,
    name: 'fake offerer name',
    address: 'fake address',
    managedVenues: [
      {
        address: '1 fake address',
        name: 'fake venue',
        publicName: 'fake venue',
        postalCode: '75000',
        city: 'Paris',
        id: 'AA',
      },
    ],
  })

  describe('render', () => {
    it('should render Venues', async () => {
      // when
      renderWithProviders(<OffererDetails {...props} />)
      await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

      // then
      expect(screen.getByText('Lieux')).toBeInTheDocument()
      expect(screen.getByText('fake venue')).toBeInTheDocument()
    })
  })
})

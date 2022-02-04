import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as pcapi from 'repository/pcapi/pcapi'
import { configureTestStore } from 'store/testUtils'

import OffererDetails from '../OffererDetails'

jest.mock('repository/pcapi/pcapi', () => ({
  getOfferer: jest.fn(),
  getBusinessUnits: jest.fn(),
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

describe('src | components | pages | Offerer | OffererDetails', () => {
  let props
  let store
  beforeEach(() => {
    props = {
      offererId: 'AA',
    }
    store = configureTestStore()
  })

  pcapi.getOfferer.mockResolvedValue({
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
    it('should render a bank instructions block if they are already provided', async () => {
      // When
      renderOffererDetails({ props, store })

      // Then
      const bankInstructions = await screen.findByText(
        'Les coordonnées bancaires ci-dessous seront attribuées à tous les lieux sans coordonnées bancaires propres :'
      )
      expect(bankInstructions).toBeInTheDocument()
    })

    it('should render Venues', async () => {
      // when
      await renderOffererDetails({ props, store })

      // then
      expect(screen.getByText('Lieux')).toBeInTheDocument()
      expect(screen.getByText('fake venue')).toBeInTheDocument()
    })

    it('should render business unit banner when offerer has invalid business unit', async () => {
      // Given
      store = configureTestStore({
        features: {
          list: [
            { isActive: true, nameKey: 'ENFORCE_BANK_INFORMATION_WITH_SIRET' },
          ],
        },
      })
      pcapi.getBusinessUnits.mockResolvedValue([
        {
          name: 'Business Unit #2',
          siret: null,
          id: 2,
          bic: 'BDFEFRPP',
          iban: 'FR9410010000000000000000022',
        },
      ])

      // When
      await renderOffererDetails({ props, store })

      // Then
      expect(
        screen.getByText(
          'Certains de vos points de remboursement ne sont pas rattachés à un SIRET. Pour continuer à percevoir vos remboursements, veuillez renseigner un SIRET de référence.'
        )
      ).toBeInTheDocument()
    })
  })
})

import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import React from 'react'

import * as pcapi from 'repository/pcapi/pcapi'

import BusinessUnitFields from '../BusinessUnitFields'

jest.mock('repository/pcapi/pcapi', () => ({
  getBusinessUnits: jest.fn(),
}))

const renderBusinessUnitField = async props => {
  const rtlReturn = await render(<BusinessUnitFields {...props} />)

  const loadingMessage = screen.queryByText('Chargement en cours ...')
  await waitFor(() => expect(loadingMessage).not.toBeInTheDocument())

  return rtlReturn
}

describe('src | Venue | BusinessUnitField', () => {
  const venue = {
    id: 'AA',
    name: 'fake venue name',
  }
  const offerer = {
    id: 'BB',
    name: 'fake offerer name',
  }
  let props
  beforeEach(() => {
    props = { readOnly: true, venue, offerer }
  })

  it('should display business unit block when offerer has at least one bu and venue is virtual', async () => {
    // Given
    pcapi.getBusinessUnits.mockResolvedValue([
      {
        name: 'Business Unit #1',
        siret: '123456789',
        id: 1,
        bic: 'BDFEFRPP',
        iban: 'FR9410010000000000000000022',
      },
    ])
    venue.isVirtual = true

    // When
    await renderBusinessUnitField(props)

    // Then
    expect(
      screen.queryByText('Coordonnées bancaires du lieu')
    ).toBeInTheDocument()
  })

  it('should not display business unit block when offerer does not have bu and venue is virtual', async () => {
    // Given
    pcapi.getBusinessUnits.mockResolvedValue([])
    venue.isVirtual = true

    // When
    await renderBusinessUnitField(props)

    // Then
    expect(
      screen.queryByText('Coordonnées bancaires du lieu')
    ).not.toBeInTheDocument()
  })
})

import { screen } from '@testing-library/react'
import React from 'react'
import * as router from 'react-router-dom'

import { VenueTypeCode } from 'apiClient/v1'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { PartnerPages, PartnerPagesProps } from '../PartnerPages'

const renderPartnerPages = (props: PartnerPagesProps) => {
  renderWithProviders(<PartnerPages {...props} />)
}

vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) ?? {}),
  useLoaderData: vi.fn(),
}))

describe('PartnerPages', () => {
  beforeEach(() => {
    vi.spyOn(router, 'useLoaderData').mockReturnValue({
      venueTypes: [{ id: VenueTypeCode.FESTIVAL, label: 'Festival' }],
    })
  })

  it('should not display select if only one venue', () => {
    renderPartnerPages({
      venues: [
        {
          ...defaultGetOffererVenueResponseModel,
          venueTypeCode: VenueTypeCode.FESTIVAL,
        },
      ],
      offerer: defaultGetOffererResponseModel,
    })

    expect(
      screen.getByRole('heading', { name: 'Votre page partenaire' })
    ).toBeInTheDocument()
    expect(
      screen.queryByLabelText(/Sélectionnez votre page partenaire/)
    ).not.toBeInTheDocument()

    expect(screen.getByText('Festival')).toBeInTheDocument()
    expect(screen.getByText('Gérer ma page')).toBeInTheDocument()
  })

  it('should display select if multiple venues', () => {
    renderPartnerPages({
      venues: [
        defaultGetOffererVenueResponseModel,
        { ...defaultGetOffererVenueResponseModel, id: 1 },
      ],
      offerer: defaultGetOffererResponseModel,
    })

    expect(
      screen.getByRole('heading', { name: 'Vos pages partenaire' })
    ).toBeInTheDocument()
    expect(
      screen.queryByLabelText(/Sélectionnez votre page partenaire/)
    ).toBeInTheDocument()
  })
})

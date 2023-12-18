import { screen } from '@testing-library/react'
import React from 'react'

import { defaultGetOffererVenueResponseModel } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { PartnerPages, PartnerPagesProps } from '../PartnerPages'

const renderPartnerPages = (props: PartnerPagesProps) => {
  renderWithProviders(<PartnerPages {...props} />)
}

describe('PartnerPages', () => {
  it('should not display select if only one venue', () => {
    renderPartnerPages({ venues: [defaultGetOffererVenueResponseModel] })

    expect(screen.getByText(/Votre page partenaire/)).toBeInTheDocument()
    expect(
      screen.queryByLabelText(/Sélectionnez votre page partenaire/)
    ).not.toBeInTheDocument()
  })

  it('should display select if multiple venues', () => {
    renderPartnerPages({
      venues: [
        defaultGetOffererVenueResponseModel,
        { ...defaultGetOffererVenueResponseModel, id: 1 },
      ],
    })

    expect(screen.getByText(/Vos pages partenaire/)).toBeInTheDocument()
    expect(
      screen.queryByLabelText(/Sélectionnez votre page partenaire/)
    ).toBeInTheDocument()
  })
})

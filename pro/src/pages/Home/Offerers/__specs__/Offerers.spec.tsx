import { screen } from '@testing-library/react'
import React from 'react'

import {
  defaultGetOffererVenueResponseModel,
  defaultGetOffererResponseModel,
} from 'commons/utils/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'

import { Offerers, OfferersProps } from '../Offerers'

const renderOfferers = (
  props: Partial<OfferersProps> = {},
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(
    <Offerers
      offererOptions={[{ label: 'name', value: 1 }]}
      selectedOfferer={defaultGetOffererResponseModel}
      isLoading={false}
      isUserOffererValidated
      venueTypes={[]}
      {...props}
    />,
    options
  )
}

describe('Offerers', () => {
  it('should display venue soft deleted', () => {
    renderOfferers()

    expect(
      screen.queryByText(
        /Votre structure a été désactivée. Pour plus d’informations sur la désactivation veuillez contacter notre support./
      )
    ).toBeInTheDocument()
  })

  it('should display the adresses', () => {
    renderOfferers({
      selectedOfferer: {
        ...defaultGetOffererResponseModel,
        managedVenues: [defaultGetOffererVenueResponseModel],
        isActive: true,
      },
    })

    expect(screen.getByText('Vos adresses')).toBeInTheDocument()
  })

  it('should display venue creation link', () => {
    renderOfferers(
      {
        selectedOfferer: {
          ...defaultGetOffererResponseModel,
          id: 200,
          managedVenues: [defaultGetOffererVenueResponseModel],
          isActive: true,
        },
      },
      { features: ['API_SIRENE_AVAILABLE'] }
    )

    expect(screen.getByText('Ajouter un lieu')).toHaveAttribute(
      'href',
      '/structures/200/lieux/creation'
    )
  })
})

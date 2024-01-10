import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'utils/apiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import Offerers, { OfferersProps } from '../Offerers'

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) ?? {}),
  useLoaderData: vi.fn(() => ({ venueTypes: [] })),
  useNavigate: () => mockNavigate,
}))

const renderOfferers = (
  props: Partial<OfferersProps> = {},
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(
    <Offerers
      receivedOffererNames={{
        offerersNames: [{ name: 'name', id: 1 }],
      }}
      onSelectedOffererChange={() => null}
      cancelLoading={() => null}
      selectedOfferer={defaultGetOffererResponseModel}
      isLoading={false}
      isUserOffererValidated
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

  it("should display the carnet d'adresses", () => {
    renderOfferers(
      {
        selectedOfferer: {
          ...defaultGetOffererResponseModel,
          managedVenues: [defaultGetOffererVenueResponseModel],
          isActive: true,
        },
      },
      { features: ['WIP_PARTNER_PAGE'] }
    )

    expect(screen.getByText('Carnet d’adresses')).toBeInTheDocument()
  })

  it('should redirect to offerer creation page when selecting "add offerer" option"', async () => {
    renderOfferers()

    await userEvent.selectOptions(
      screen.getByLabelText('Sélectionner une structure'),
      '+ Ajouter une structure'
    )

    expect(mockNavigate).toHaveBeenCalledWith('/structures/creation')
  })
})

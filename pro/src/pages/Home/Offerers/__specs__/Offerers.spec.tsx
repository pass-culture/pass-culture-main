import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

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
        managedVenues: [
          {
            ...defaultGetOffererVenueResponseModel,
            id: 1,
            name: 'Ma structure permanente',
            isPermanent: true,
          },
          {
            ...defaultGetOffererVenueResponseModel,
            id: 2,
            name: 'Ma seconde structure',
            isPermanent: false,
          },
        ],
        isActive: true,
      },
    })
    expect(
      screen.getByRole('heading', { level: 3, name: /Ma structure permanente/ })
    ).toBeInTheDocument()
    expect(screen.getByText('Vos adresses')).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { level: 3, name: /Ma seconde structure/ })
    ).toBeInTheDocument()
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

    expect(
      screen.getByRole('link', { name: 'Ajouter un lieu' })
    ).toHaveAttribute('href', '/structures/200/lieux/creation')
  })

  it('should display the new informative modal for offer address', async () => {
    renderOfferers(
      {
        selectedOfferer: {
          ...defaultGetOffererResponseModel,
          id: 200,
          managedVenues: [defaultGetOffererVenueResponseModel],
          isActive: true,
        },
      },
      { features: ['WIP_ENABLE_OFFER_ADDRESS'] }
    )

    const addVenueButton = screen.getByRole('button', {
      name: 'Ajouter un lieu',
    })

    expect(addVenueButton).toBeInTheDocument()

    await userEvent.click(addVenueButton)

    expect(
      screen.getByRole('heading', {
        level: 2,
        name: 'Il n’est plus nécessaire de créer des lieux',
      })
    ).toBeInTheDocument()
  })
})

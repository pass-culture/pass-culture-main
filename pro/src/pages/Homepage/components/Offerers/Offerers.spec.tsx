import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'commons/utils/factories/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'

import { Offerers, OfferersProps } from './Offerers'

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
      screen.getByRole('link', { name: 'Ajouter une structure' })
    ).toHaveAttribute('href', '/parcours-inscription/structure')
  })

  it('should display the new informative modal for offer address', async () => {
    renderOfferers({
      selectedOfferer: {
        ...defaultGetOffererResponseModel,
        id: 200,
        managedVenues: [defaultGetOffererVenueResponseModel],
        isActive: true,
      },
    })

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

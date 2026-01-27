import { screen } from '@testing-library/react'

import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { NewHomepage } from './NewHomepage'

const renderNewHomepage = (options?: RenderWithProvidersOptions) => {
  const user = sharedCurrentUserFactory()
  renderWithProviders(<NewHomepage />, {
    user,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedVenue: defaultGetOffererVenueResponseModel,
      },
      offerer: {
        currentOfferer: {
          ...defaultGetOffererResponseModel,
          managedVenues: [defaultGetOffererVenueResponseModel],
        },
      },
    },
    ...options,
  })
}

describe('NewHomepage', () => {
  it('should display the selected venue public name in the title', () => {
    renderNewHomepage()
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      'Votre espace Nom public de la structure'
    )
  })
})

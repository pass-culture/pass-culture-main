import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { FieldEnum, FormatEnum, NatureEnum } from '@/apiClient/v1'
import { routesIndividualOfferV2 } from '@/app/AppRouter/subroutesIndividualOfferV2'
import type { NFDState } from '@/commons/store/nfd/reducer'
import { createStore, rootStore } from '@/commons/store/store'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component as IndividualOfferV2Description } from './IndividualOfferV2Description'

vi.mock('@/commons/auth/withUserPermissions', () => ({
  withUserPermissions: (_permissions: unknown, loader: unknown) => loader,
}))

vi.mock('@/commons/hooks/useMusicTypes', () => ({
  useMusicTypes: () => ({ musicTypes: [] }),
}))

const renderIndividualOfferV2Description = (
  selection: NFDState = {
    nature: NatureEnum.BIEN,
    format: FormatEnum.LIVRE_PAPIER,
  }
) => {
  vi.spyOn(api, 'getCapabilities').mockResolvedValue({
    capabilities: [FieldEnum.TITLE],
    mandatoryFields: [FieldEnum.TITLE],
  })

  vi.spyOn(rootStore, 'getState').mockReturnValue(
    createStore({ nfd: selection }).store.getState()
  )

  return renderWithProviders(null, {
    initialRouterEntries: ['/offre/individuelle/v2/creation/description'],
    routes: [
      {
        path: '/offre/individuelle/v2/creation/description',
        hydrateFallbackElement: <div>Chargement</div>,
        loader: routesIndividualOfferV2.find(
          (route) => route.path === 'creation/description'
        )?.loader,
        element: <IndividualOfferV2Description />,
      },
      {
        path: '/offre/individuelle/v2/creation/nature-format-domaine',
        element: <h1>Nature et format</h1>,
      },
    ],
    storeOverrides: {
      nfd: selection,
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: 1,
        }),
      },
    },
  })
}

describe('<IndividualOfferV2Description />', () => {
  it.each([
    {},
    { nature: NatureEnum.BIEN },
    { format: FormatEnum.LIVRE_PAPIER },
  ])(
    'should redirect when nature or format is missing (%o)',
    async (selection) => {
      renderIndividualOfferV2Description(selection)

      expect(
        await screen.findByRole('heading', { name: 'Nature et format' })
      ).toBeInTheDocument()
      expect(screen.queryByLabelText(/Titre du bien/)).not.toBeInTheDocument()
      expect(api.getCapabilities).not.toHaveBeenCalled()
    }
  )

  it('should display the description when nature and format are selected', async () => {
    renderIndividualOfferV2Description()

    expect(await screen.findByLabelText(/Titre du bien/)).toBeInTheDocument()
    expect(
      screen.queryByRole('heading', { name: 'Nature et format' })
    ).not.toBeInTheDocument()
  })

  it('should have no accessibility violations', async () => {
    const { container } = renderIndividualOfferV2Description()
    await screen.findByLabelText(/Titre du bien/)

    expect(await axe(container)).toHaveNoViolations()
  })
})

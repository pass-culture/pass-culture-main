import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { FieldEnum, FormatEnum, NatureEnum } from '@/apiClient/v1'
import { routesIndividualOfferV2 } from '@/app/AppRouter/subroutesIndividualOfferV2'
import type { NFDState } from '@/commons/store/nfd/reducer'
import { createStore, rootStore } from '@/commons/store/store'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOfferV2 } from '../IndividualOfferV2'
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
  },
  capabilities: FieldEnum[] = [FieldEnum.TITLE_BIEN]
) => {
  vi.spyOn(api, 'getCapabilities').mockResolvedValue({
    capabilities,
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
  it.each<NFDState>([
    { nature: null, format: null },
    { nature: NatureEnum.BIEN, format: null },
    { nature: null, format: FormatEnum.LIVRE_PAPIER },
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

  it('should display the image upload zone when the offer can have an image', async () => {
    renderIndividualOfferV2Description(undefined, [
      FieldEnum.TITLE_BIEN,
      FieldEnum.IMAGE,
    ])

    const input = await screen.findByLabelText(/Ajoutez une image/)
    expect(input).toHaveAttribute('type', 'file')
    expect(input).not.toHaveAttribute('multiple')
  })

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

  it('should display an error and not save when a mandatory field is empty', async () => {
    vi.spyOn(api, 'createOffer')
    renderIndividualOfferV2Description()

    const titleInput = await screen.findByLabelText(/Titre du bien/)
    await userEvent.click(titleInput)
    await userEvent.tab()

    expect(
      await screen.findByText('Veuillez renseigner un titre')
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(api.createOffer).not.toHaveBeenCalled()
  })

  describe('with an existing offer and a new nature/format', () => {
    const offer = getIndividualOfferFactory({
      id: 12,
      name: 'Ancien livre',
      nature: NatureEnum.BIEN,
      format: FormatEnum.LIVRE_PAPIER,
      capabilities: [FieldEnum.TITLE_BIEN],
      mandatoryFields: [FieldEnum.TITLE],
      hasStocks: true,
    })

    const renderWithOffer = (nfd: NFDState) =>
      renderWithProviders(null, {
        initialRouterEntries: [
          '/offre/individuelle/v2/12/creation/description',
        ],
        routes: [
          {
            path: '/offre/individuelle/v2/:offerId/creation',
            element: <IndividualOfferV2 />,
            children: [
              {
                path: 'description',
                element: <IndividualOfferV2Description />,
              },
              { path: 'tarifs-modalites', element: <h2>Tarifs</h2> },
            ],
          },
        ],
        storeOverrides: {
          nfd,
          user: {
            currentUser: sharedCurrentUserFactory(),
            selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
          },
        },
      })

    beforeEach(() => {
      vi.spyOn(api, 'getOffer').mockResolvedValue(offer)
      vi.spyOn(api, 'getCapabilities').mockResolvedValue({
        capabilities: [FieldEnum.TITLE_BIEN],
        mandatoryFields: [FieldEnum.TITLE],
      })
      vi.spyOn(api, 'getStocks').mockResolvedValue({
        stocks: [{ id: 1 }, { id: 2 }] as never,
        totalStockCount: 2,
        editedStockCount: 0,
      })
      vi.spyOn(api, 'deleteStocks').mockResolvedValue(undefined as never)
      vi.spyOn(api, 'deleteThumbnail').mockResolvedValue(undefined as never)
      vi.spyOn(api, 'patchOffer').mockResolvedValue({
        ...offer,
        format: FormatEnum.CD,
      })
    })

    it('should display the offer data when nature/format are unchanged', async () => {
      renderWithOffer({ nature: null, format: null })

      expect(await screen.findByLabelText(/Titre du bien/)).toHaveValue(
        'Ancien livre'
      )
    })

    it('should display an empty form and reset the offer on save', async () => {
      const { store } = renderWithOffer({
        nature: NatureEnum.BIEN,
        format: FormatEnum.CD,
      })

      const titleInput = await screen.findByLabelText(/Titre du bien/)
      expect(titleInput).toHaveValue('')
      expect(api.getCapabilities).toHaveBeenCalledWith({
        query: { nature: NatureEnum.BIEN, format: FormatEnum.CD },
      })

      await userEvent.type(titleInput, 'Nouveau CD')
      await userEvent.click(
        screen.getByRole('button', { name: 'Étape suivante' })
      )

      expect(
        await screen.findByRole('heading', { name: 'Tarifs' })
      ).toBeInTheDocument()
      expect(api.deleteStocks).toHaveBeenCalledWith({
        path: { offer_id: 12 },
        body: { ids_to_delete: [1, 2] },
      })
      expect(api.patchOffer).toHaveBeenCalledWith({
        path: { offer_id: 12 },
        body: expect.objectContaining({
          nature: NatureEnum.BIEN,
          format: FormatEnum.CD,
          name: 'Nouveau CD',
          description: null,
          withdrawalType: null,
        }),
      })
      expect(store.getState().nfd).toEqual({ nature: null, format: null })
    })
  })
})

import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import type { CollectiveOfferTemplateResponseModel } from '@/apiClient/v1'
import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import * as createFromTemplateUtils from '@/commons/core/OfferEducational/utils/createOfferFromTemplate'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { collectiveOfferTemplateFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferSelectionDuplication } from './CollectiveOfferSelectionDuplication'

function renderCollectiveOfferSelectionDuplication() {
  renderWithProviders(<CollectiveOfferSelectionDuplication />, {
    storeOverrides: {
      user: {
        selectedPartnerVenue: makeGetVenueResponseModel({ id: 2 }),
      },
    },
  })
}

vi.mock('@/apiClient/api', () => ({
  api: {
    getCollectiveOfferTemplates: vi.fn(),
  },
}))

vi.mock(
  '@/commons/core/OfferEducational/utils/createOfferFromTemplate',
  () => ({
    createOfferFromTemplate: vi.fn(),
  })
)

const offers: CollectiveOfferTemplateResponseModel[] = [
  collectiveOfferTemplateFactory(),
  collectiveOfferTemplateFactory(),
]

describe('CollectiveOfferConfirmation', () => {
  const snackBarError = vi.fn()

  beforeEach(() => {
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      success: vi.fn(),
      error: snackBarError,
    }))
    vi.spyOn(api, 'getCollectiveOfferTemplates').mockResolvedValue(offers)
  })

  it('should render selection duplication page', async () => {
    renderCollectiveOfferSelectionDuplication()

    await waitForElementToBeRemoved(() =>
      screen.queryAllByTestId('skeleton-loader')
    )

    expect(
      screen.getByText('Rechercher l’offre vitrine à dupliquer')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Les dernières offres vitrines créées')
    ).toBeInTheDocument()

    expect(api.getCollectiveOfferTemplates).toHaveBeenCalledTimes(1)

    expect(await screen.findByText('Offre vitrine 2')).toBeInTheDocument()
  })

  it('should display list of offers matching user search', async () => {
    renderCollectiveOfferSelectionDuplication()

    expect(
      await screen.findByText('Les dernières offres vitrines créées')
    ).toBeInTheDocument()

    const searchField = screen.getByRole('searchbox')

    await userEvent.type(searchField, 'Le nom de l’offre 3')

    await userEvent.click(screen.getByRole('button', { name: 'Rechercher' }))

    expect(api.getCollectiveOfferTemplates).toHaveBeenLastCalledWith({
      query: {
        name: 'Le nom de l’offre 3',
        offererId: 1,
        status: [
          CollectiveOfferDisplayedStatus.PUBLISHED,
          CollectiveOfferDisplayedStatus.HIDDEN,
          CollectiveOfferDisplayedStatus.ENDED,
        ],
        venueId: 2,
        periodBeginningDate: null,
        periodEndingDate: null,
        format: null,
        locationType: null,
        offererAddressId: null,
      },
    })
  })

  it('should create a bookable offer after clicking a template offer an offer', async () => {
    renderCollectiveOfferSelectionDuplication()

    vi.spyOn(createFromTemplateUtils, 'createOfferFromTemplate')

    await waitFor(() =>
      expect(
        screen.getByText('Les dernières offres vitrines créées')
      ).toBeInTheDocument()
    )

    expect(api.getCollectiveOfferTemplates).toHaveBeenCalledTimes(1)

    const inputOffer = await waitFor(() =>
      screen.getByRole('button', { name: offers[0].name })
    )
    await userEvent.click(inputOffer)

    expect(createFromTemplateUtils.createOfferFromTemplate).toHaveBeenCalled()
  })

  it('should display message when no offer', async () => {
    vi.spyOn(api, 'getCollectiveOfferTemplates').mockResolvedValue([])

    renderCollectiveOfferSelectionDuplication()

    await waitFor(() =>
      expect(
        screen.getByText('Les dernières offres vitrines créées')
      ).toBeInTheDocument()
    )

    expect(api.getCollectiveOfferTemplates).toHaveBeenCalledTimes(1)

    const searchIcon = screen.getByRole('img', {
      name: 'Illustration de recherche',
    })

    expect(
      screen.getByText('Les dernières offres vitrines créées')
    ).toBeInTheDocument()
    expect(searchIcon).toBeInTheDocument()
    expect(
      screen.getByText('Aucune offre trouvée pour votre recherche')
    ).toBeInTheDocument()
  })

  it('should display an error message when there is an api error', async () => {
    vi.spyOn(api, 'getCollectiveOfferTemplates').mockRejectedValueOnce(
      'Nous avons rencontré un problème lors de la récupération des données.'
    )

    renderCollectiveOfferSelectionDuplication()

    await waitFor(() =>
      expect(
        screen.getByText(/Les dernières offres vitrines créées/)
      ).toBeInTheDocument()
    )

    const searchField = screen.getByRole('searchbox', {
      name: 'Rechercher l’offre vitrine à dupliquer',
    })

    await userEvent.type(searchField, 'Le nom de l’offre 3')
    await userEvent.click(screen.getByRole('button', { name: 'Rechercher' }))

    await waitFor(() =>
      expect(snackBarError).toHaveBeenNthCalledWith(
        1,
        'Nous avons rencontré un problème lors de la récupération des données.'
      )
    )
  })
})

import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'

import { api } from 'apiClient/api'
import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseModel,
} from 'apiClient/v1'
import * as createFromTemplateUtils from 'commons/core/OfferEducational/utils/createOfferFromTemplate'
import * as useNotification from 'commons/hooks/useNotification'
import { collectiveOfferFactory } from 'commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { CollectiveOfferSelectionDuplication } from '../CollectiveOfferSelectionDuplication'

interface InitialValuesProps {
  searchFilter: string
  templateOfferId: string
}

const renderCollectiveOfferSelectionDuplication = ({
  initialValues,
  onSubmit,
}: {
  initialValues: InitialValuesProps
  onSubmit: () => void
}) => {
  renderWithProviders(
    <Formik initialValues={initialValues} onSubmit={onSubmit}>
      <CollectiveOfferSelectionDuplication />
    </Formik>
  )
}

vi.mock('apiClient/api', () => ({
  api: {
    getCollectiveOffers: vi.fn(),
  },
}))

vi.mock('commons/core/OfferEducational/utils/createOfferFromTemplate', () => ({
  createOfferFromTemplate: vi.fn(),
}))

describe('CollectiveOfferConfirmation', () => {
  let initialValues = { searchFilter: 'string', templateOfferId: 'string' }
  const onSubmit = vi.fn()
  const notifyError = vi.fn()

  beforeEach(() => {
    const offers: CollectiveOfferResponseModel[] = [
      collectiveOfferFactory(),
      collectiveOfferFactory(),
    ]

    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      success: vi.fn(),
      error: notifyError,
      information: vi.fn(),
      pending: vi.fn(),
      close: vi.fn(),
    }))
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue(offers)
  })

  it('should render selection duplication page', async () => {
    renderCollectiveOfferSelectionDuplication({
      initialValues,
      onSubmit,
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByText('Rechercher l’offre vitrine à dupliquer')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Les dernières offres vitrines créées')
    ).toBeInTheDocument()

    expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)

    expect(await screen.findByText('offer name 2')).toBeInTheDocument()
  })

  it('should display list of offers matching user search', async () => {
    renderCollectiveOfferSelectionDuplication({ initialValues, onSubmit })

    expect(
      await screen.findByText('Les dernières offres vitrines créées')
    ).toBeInTheDocument()

    const searchField = screen.getByRole('searchbox')

    await userEvent.type(searchField, 'Le nom de l’offre 3')

    await userEvent.click(screen.getByRole('button', { name: 'Rechercher' }))

    expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
      'Le nom de l’offre 3',
      undefined,
      [
        CollectiveOfferDisplayedStatus.ACTIVE,
        CollectiveOfferDisplayedStatus.INACTIVE,
        CollectiveOfferDisplayedStatus.ENDED,
      ],
      undefined,
      undefined,
      undefined,
      undefined,
      'template',
      undefined
    )
  })

  it('should select an offer', async () => {
    renderCollectiveOfferSelectionDuplication({ initialValues, onSubmit })

    await waitFor(() =>
      expect(
        screen.getByText('Les dernières offres vitrines créées')
      ).toBeInTheDocument()
    )

    expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)

    const inputOffer = await waitFor(() => screen.getAllByRole('radio')[0])
    await userEvent.click(inputOffer)

    expect(inputOffer).toBeChecked()
  })

  it('should redirect on submit button and offer selected', async () => {
    vi.spyOn(createFromTemplateUtils, 'createOfferFromTemplate')
    renderCollectiveOfferSelectionDuplication({ initialValues, onSubmit })

    await waitFor(() =>
      expect(
        screen.getByText('Les dernières offres vitrines créées')
      ).toBeInTheDocument()
    )

    const inputOffer = await waitFor(() => screen.getAllByRole('radio')[0])
    await userEvent.click(inputOffer)

    const buttonNextStep = screen.getByText('Étape suivante')
    await userEvent.click(buttonNextStep)

    expect(createFromTemplateUtils.createOfferFromTemplate).toHaveBeenCalled()
  })

  it('should display message when no offer', async () => {
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue([])
    renderCollectiveOfferSelectionDuplication({ initialValues, onSubmit })

    await waitFor(() =>
      expect(
        screen.getByText('Les dernières offres vitrines créées')
      ).toBeInTheDocument()
    )

    expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)

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
    vi.spyOn(api, 'getCollectiveOffers').mockRejectedValueOnce('')
    renderCollectiveOfferSelectionDuplication({ initialValues, onSubmit })

    await waitFor(() =>
      expect(
        screen.getByText('Les dernières offres vitrines créées')
      ).toBeInTheDocument()
    )

    const searchField = screen.getByRole('searchbox', {
      name: 'Rechercher l’offre vitrine à dupliquer',
    })

    await userEvent.type(searchField, 'Le nom de l’offre 3')

    await userEvent.click(screen.getByRole('button', { name: 'Rechercher' }))
    await waitFor(() =>
      expect(notifyError).toHaveBeenNthCalledWith(
        1,
        'Nous avons rencontré un problème lors de la récupération des données.'
      )
    )
  })
})

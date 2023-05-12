import { screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import { api } from 'apiClient/api'
import * as createFromTemplateUtils from 'core/OfferEducational/utils/createOfferFromTemplate'
import { Offer } from 'core/Offers/types'
import * as useNotification from 'hooks/useNotification'
import { collectiveOfferFactory } from 'pages/CollectiveOffers/utils/collectiveOffersFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferSelectionDuplication from '../CollectiveOfferSelectionDuplicationScreen'

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

jest.mock('apiClient/api', () => ({
  api: {
    getCollectiveOffers: jest.fn(),
  },
}))

jest.mock('core/OfferEducational/utils/createOfferFromTemplate', () => ({
  createOfferFromTemplate: jest.fn(),
}))

describe('CollectiveOfferConfirmation', () => {
  let initialValues: { searchFilter: string; templateOfferId: string }
  const onSubmit = jest.fn()
  const notifyError = jest.fn()

  beforeEach(() => {
    const offers: Offer[] = [collectiveOfferFactory(), collectiveOfferFactory()]

    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      success: jest.fn(),
      error: notifyError,
      information: jest.fn(),
      pending: jest.fn(),
      close: jest.fn(),
    }))
    jest
      .spyOn(api, 'getCollectiveOffers')
      // @ts-expect-error FIX ME : will be fix PC-19976
      .mockReturnValue(offers)
  })

  it('should render selection duplication page', async () => {
    renderCollectiveOfferSelectionDuplication({
      initialValues,
      onSubmit,
    })

    expect(
      screen.getByText('Séléctionner l’offre vitrine à dupliquer')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Les dernières offres vitrines créées')
    ).toBeInTheDocument()

    expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)

    await waitFor(() =>
      expect(screen.getByText('offer name 2')).toBeInTheDocument()
    )
  })

  it('should display list of offers matching user search', async () => {
    renderCollectiveOfferSelectionDuplication({ initialValues, onSubmit })

    await waitFor(() =>
      expect(
        screen.getByText('Les dernières offres vitrines créées')
      ).toBeInTheDocument()
    )

    const searchField = screen.getByPlaceholderText(
      'Rechercher une offre vitrine'
    )

    await userEvent.type(searchField, 'Le nom de l’offre 3')

    await userEvent.click(
      screen.getByRole('button', { name: /Button de recherche/i })
    )

    expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
      'Le nom de l’offre 3',
      undefined,
      undefined,
      undefined,
      undefined,
      undefined,
      undefined,
      undefined,
      'template'
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
    await jest.spyOn(createFromTemplateUtils, 'createOfferFromTemplate')
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
    await jest
      .spyOn(api, 'getCollectiveOffers')
      // @ts-expect-error FIX ME : will be fix PC-19976
      .mockReturnValue([])
    renderCollectiveOfferSelectionDuplication({ initialValues, onSubmit })

    await waitFor(() =>
      expect(
        screen.getByText('Les dernières offres vitrines créées')
      ).toBeInTheDocument()
    )

    expect(api.getCollectiveOffers).toHaveBeenCalledTimes(1)

    const searchIcon = screen.getByAltText('Illustration de recherche')

    expect(
      screen.getByText('Les dernières offres vitrines créées')
    ).toBeInTheDocument()
    expect(searchIcon).toBeInTheDocument()
    expect(
      screen.getByText('Aucune offre trouvée pour votre recherche')
    ).toBeInTheDocument()
  })

  it('should display an error message when there is an api error', async () => {
    jest.spyOn(api, 'getCollectiveOffers').mockRejectedValueOnce('')
    renderCollectiveOfferSelectionDuplication({ initialValues, onSubmit })

    await waitFor(() =>
      expect(
        screen.getByText('Les dernières offres vitrines créées')
      ).toBeInTheDocument()
    )

    const searchField = screen.getByPlaceholderText(
      'Rechercher une offre vitrine'
    )

    await userEvent.type(searchField, 'Le nom de l’offre 3')

    await userEvent.click(
      screen.getByRole('button', { name: /Button de recherche/i })
    )
    await waitFor(() =>
      expect(notifyError).toHaveBeenNthCalledWith(
        1,
        'Nous avons rencontré un problème lors de la récupération des données.'
      )
    )
  })

  it('should display error when offer not selected', async () => {
    renderCollectiveOfferSelectionDuplication({ initialValues, onSubmit })

    await waitFor(() =>
      expect(
        screen.getByText('Les dernières offres vitrines créées')
      ).toBeInTheDocument()
    )

    const buttonNextStep = screen.getByText('Étape suivante')
    await userEvent.click(buttonNextStep)

    await waitFor(() =>
      expect(notifyError).toHaveBeenNthCalledWith(
        1,
        'Vous devez séléctionner une offre vitrine à dupliquer'
      )
    )
  })
})

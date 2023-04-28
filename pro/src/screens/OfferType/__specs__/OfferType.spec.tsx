import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { CancelablePromise, GetOffererResponseModel } from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import * as useNotification from 'hooks/useNotification'
import { collectiveOfferFactory } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferType from '../OfferType'

const mockLogEvent = jest.fn()

jest.mock('apiClient/api', () => ({
  api: {
    listOfferersNames: jest.fn(),
    canOffererCreateEducationalOffer: jest.fn(),
    getCollectiveOffers: jest.fn(),
    getOfferer: jest.fn(),
  },
}))

const renderOfferTypes = async (storeOverrides: any, structureId?: string) => {
  renderWithProviders(
    <Routes>
      <Route path="/creation" element={<OfferType />} />
      <Route
        path="/offre/creation/collectif"
        element={<div>Création collectif</div>}
      />
      <Route
        path="/offre/creation/collectif/vitrine"
        element={<div>Création vitrine collectif</div>}
      />
      <Route
        path="/offre/individuelle/creation/informations"
        element={<div>Création individuel</div>}
      />
      <Route
        path="/offre/creation/collectif/selection"
        element={<div>Sélection collectif</div>}
      />
    </Routes>,
    {
      storeOverrides,
      initialRouterEntries: [
        `/creation${structureId ? `?structure=${structureId}` : ''}`,
      ],
    }
  )

  await waitFor(() => {
    expect(api.listOfferersNames).toHaveBeenCalled()
  })
  await waitFor(() => {
    expect(api.canOffererCreateEducationalOffer).toHaveBeenCalled()
  })
  await waitFor(() => {
    expect(api.getCollectiveOffers).toHaveBeenCalled()
  })
}

describe('screens:OfferIndividual::OfferType', () => {
  let store: any
  beforeAll(() => {
    jest.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        { id: 'A1', nonHumanizedId: 1, name: 'Ma super structure' },
      ],
    })
    jest.spyOn(api, 'getCollectiveOffers').mockResolvedValue([])
    jest.spyOn(api, 'canOffererCreateEducationalOffer').mockResolvedValue()
  })
  beforeEach(() => {
    store = {
      user: {
        initialized: true,
        currentUser: {
          isAdmin: false,
          email: 'email@example.com',
        },
      },
      features: {
        list: [
          {
            nameKey: 'WIP_DUPLICATE_OFFER_SELECTION',
            isActive: true,
          },
        ],
        initialized: true,
      },
    }

    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should render the component with button', async () => {
    renderOfferTypes(store)

    expect(
      screen.getByRole('heading', { name: 'Créer une offre' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('radio', { name: 'Au grand public' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Annuler et quitter' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Étape suivante' })
    ).toBeInTheDocument()
  })

  it('should render action bar buttons ', async () => {
    renderOfferTypes(store)

    expect(
      screen.getByRole('link', { name: 'Annuler et quitter' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Étape suivante' })
    ).toBeInTheDocument()
  })

  it('should select collective offer', async () => {
    renderOfferTypes(store)

    expect(
      screen.queryByRole('heading', { name: 'Quel est le type de l’offre ?' })
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )
    await userEvent.click(
      screen.getByRole('radio', {
        name: 'Une offre réservable Cette offre a une date et un prix. Vous pouvez choisir de la rendre visible par tous les établissements scolaires ou par un seul.',
      })
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(screen.getByText('Création collectif')).toBeInTheDocument()
  })

  it('should select template offer', async () => {
    jest.spyOn(api, 'listOfferersNames').mockResolvedValueOnce({
      offerersNames: [
        { id: 'A1', nonHumanizedId: 1, name: 'Ma super structure' },
        { id: 'A2', nonHumanizedId: 2, name: 'Ma super structure #2' },
      ],
    })
    renderOfferTypes(store)

    expect(
      screen.queryByRole('heading', { name: 'Quel est le type de l’offre ?' })
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )

    await userEvent.click(
      screen.getByRole('radio', {
        name: 'Une offre vitrine Cette offre n’est pas réservable. Elle n’a ni date, ni prix et permet aux enseignants de vous contacter pour co-construire une offre adaptée. Vous pourrez facilement la dupliquer pour chaque enseignant intéressé.',
      })
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(screen.getByText('Création vitrine collectif')).toBeInTheDocument()
  })

  it('should display non eligible banner if offerer can not create collective offer', async () => {
    jest.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        { id: 'A1', nonHumanizedId: 1, name: 'Ma super structure' },
      ],
    })
    jest.spyOn(api, 'canOffererCreateEducationalOffer').mockRejectedValue({})
    renderOfferTypes(store)

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )
    expect(api.canOffererCreateEducationalOffer).toHaveBeenCalledTimes(1)

    expect(
      await screen.findByText(
        'Pour proposer des offres à destination d’un groupe scolaire, vous devez être référencé auprès du ministère de l’Éducation Nationale et du ministère de la Culture.'
      )
    ).toBeInTheDocument()
  })

  it('should display individual offer choices', async () => {
    renderOfferTypes(store)

    expect(screen.getByText('Un bien physique')).toBeInTheDocument()
    expect(screen.getByText('Un bien numérique')).toBeInTheDocument()
    expect(screen.getByText('Un évènement physique daté')).toBeInTheDocument()
    expect(screen.getByText('Un évènement numérique daté')).toBeInTheDocument()
  })

  const individualChoices = [
    {
      buttonClicked: 'Un bien physique',
      expectedSearch: 'PHYSICAL_GOOD',
    },
    {
      buttonClicked: 'Un bien numérique',
      expectedSearch: 'VIRTUAL_GOOD',
    },
    {
      buttonClicked: 'Un évènement physique daté',
      expectedSearch: 'PHYSICAL_EVENT',
    },
    {
      buttonClicked: 'Un évènement numérique daté',
      expectedSearch: 'VIRTUAL_EVENT',
    },
  ]
  it.each(individualChoices)(
    'should select and redirect fine case : %s',
    async ({ buttonClicked, expectedSearch }) => {
      renderOfferTypes(store)

      await userEvent.click(screen.getByText(buttonClicked))

      await userEvent.click(
        screen.getByRole('button', { name: 'Étape suivante' })
      )

      expect(screen.getByText('Création individuel')).toBeInTheDocument()
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_OFFER_FORM_NAVIGATION,
        {
          from: 'OfferFormHomepage',
          offerType: expectedSearch,
          to: 'informations',
          used: 'StickyButtons',
        }
      )
    }
  )

  it('should select duplicate template offer', async () => {
    jest.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        { id: 'A1', nonHumanizedId: 1, name: 'Ma super structure' },
      ],
    })
    jest.spyOn(api, 'canOffererCreateEducationalOffer').mockResolvedValue()
    const offersRecap = [collectiveOfferFactory()]
    jest
      .spyOn(api, 'getCollectiveOffers')
      // @ts-expect-error FIX ME
      .mockResolvedValue(offersRecap)

    renderOfferTypes(store)

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )

    expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
      undefined,
      undefined,
      undefined,
      undefined,
      undefined,
      undefined,
      undefined,
      undefined,
      'template'
    )

    await userEvent.click(
      screen.getByRole('radio', {
        name: 'Une offre réservable Cette offre a une date et un prix. Vous pouvez choisir de la rendre visible par tous les établissements scolaires ou par un seul.',
      })
    )

    expect(
      screen.queryByRole('heading', {
        name: 'Créer une nouvelle offre ou dupliquer une offre ?',
      })
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('radio', {
        name: 'Dupliquer les informations d’une d’offre vitrine Créez une offre réservable en dupliquant les informations d’une offre vitrine existante.',
      })
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(screen.getByText('Sélection collectif')).toBeInTheDocument()
  })

  it('should display error message if trying to duplicate without template offer', async () => {
    jest.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        { id: 'A1', nonHumanizedId: 1, name: 'Ma super structure' },
      ],
    })
    jest.spyOn(api, 'canOffererCreateEducationalOffer').mockResolvedValue()
    jest.spyOn(api, 'getCollectiveOffers').mockResolvedValue([])
    const notifyError = jest.fn()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...jest.requireActual('hooks/useNotification'),
      error: notifyError,
    }))

    renderOfferTypes(store)

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )

    await userEvent.click(
      screen.getByRole('radio', {
        name: 'Une offre réservable Cette offre a une date et un prix. Vous pouvez choisir de la rendre visible par tous les établissements scolaires ou par un seul.',
      })
    )

    await userEvent.click(
      screen.getByRole('radio', {
        name: 'Dupliquer les informations d’une d’offre vitrine Créez une offre réservable en dupliquant les informations d’une offre vitrine existante.',
      })
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(notifyError).toHaveBeenCalledWith(
      'Vous devez créer une offre vitrine avant de pouvoir utiliser cette fonctionnalité'
    )
  })

  it('should log when cancelling ', async () => {
    renderOfferTypes(store)

    await userEvent.click(
      screen.getByRole('link', { name: 'Annuler et quitter' })
    )
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_CANCEL_OFFER_CREATION
    )
  })

  it('should display validation banner if structure not validated for collective offer ', async () => {
    jest.spyOn(api, 'getOfferer').mockResolvedValue({
      isValidated: false,
    } as GetOffererResponseModel)
    renderOfferTypes(store, '123')

    expect(
      await screen.queryByText(
        'Votre structure est en cours de validation par les équipes pass Culture.'
      )
    ).not.toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )

    expect(
      await screen.findByText(
        'Votre structure est en cours de validation par les équipes pass Culture.'
      )
    ).toBeInTheDocument()
  })

  it('should render loader while fetching data', async () => {
    jest
      .spyOn(api, 'getOfferer')
      .mockResolvedValueOnce(
        new CancelablePromise(resolve =>
          setTimeout(() => resolve({} as GetOffererResponseModel), 500)
        )
      )

    renderOfferTypes(store, '123')

    expect(await screen.findByText('Chargement en cours')).toBeInTheDocument()
  })
})

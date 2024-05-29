import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { CancelablePromise, GetOffererResponseModel } from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'
import * as useNotification from 'hooks/useNotification'
import {
  collectiveOfferFactory,
  defaultDMSApplicationForEAC,
} from 'utils/collectiveApiFactories'
import {
  defaultGetOffererVenueResponseModel,
  defaultGetOffererResponseModel,
  getOffererNameFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { OfferTypeScreen } from '../OfferType'

const mockLogEvent = vi.fn()

vi.mock('@firebase/remote-config', () => ({
  getValue: () => ({ asBoolean: () => true }),
}))

vi.mock('apiClient/api', () => ({
  api: {
    listOfferersNames: vi.fn(),
    canOffererCreateEducationalOffer: vi.fn(),
    getCollectiveOffers: vi.fn(),
    getOfferer: vi.fn(),
    getVenue: vi.fn(),
    getCategories: vi.fn(),
  },
}))

const renderOfferTypes = (structureId?: string, venueId?: string) => {
  renderWithProviders(
    <Routes>
      <Route path="/creation" element={<OfferTypeScreen />} />
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
      user: sharedCurrentUserFactory(),
      initialRouterEntries: [
        `/creation${
          structureId
            ? `?structure=${structureId}${venueId ? `&lieu=${venueId}` : ''}`
            : ''
        }`,
      ],
    }
  )
}

describe('OfferType', () => {
  beforeEach(() => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        getOffererNameFactory({
          id: 1,
          name: 'Ma super structure',
        }),
      ],
    })
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue([])

    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      isValidated: true,
    })

    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should render the component with button', async () => {
    renderOfferTypes()

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

    // Loads individual offer buttons by default
    expect(await screen.findByText('Un bien physique')).toBeInTheDocument()
  })

  it('should select collective offer', async () => {
    renderOfferTypes()

    expect(
      await screen.findByRole('heading', { name: 'Votre offre est :' })
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )

    await userEvent.click(
      await screen.findByRole('radio', {
        name: 'Une offre réservable Cette offre a une date et un prix. Elle doit être associée à un établissement scolaire avec lequel vous avez préalablement échangé.',
      })
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(screen.getByText('Création collectif')).toBeInTheDocument()
  })

  it('should select template offer', async () => {
    renderOfferTypes()

    expect(
      await screen.findByRole('heading', { name: 'Votre offre est :' })
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )

    await userEvent.click(
      await screen.findByRole('radio', {
        name: 'Une offre vitrine Cette offre n’est pas réservable. Elle permet aux enseignants de vous contacter pour co-construire une offre adaptée. Vous pourrez facilement la dupliquer pour chaque enseignant intéressé.',
      })
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(screen.getByText('Création vitrine collectif')).toBeInTheDocument()
  })

  it('should display non eligible banner if offerer can not create collective offer', async () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      allowedOnAdage: false,
    })

    renderOfferTypes()

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )

    expect(
      await screen.findByText(
        'Pour proposer des offres à destination d’un groupe scolaire, vous devez être référencé auprès du ministère de l’Éducation Nationale et du ministère de la Culture.'
      )
    ).toBeInTheDocument()
  })

  it('should display dms application banner if offerer can not create collective offer but has a dms application', async () => {
    const offerer: GetOffererResponseModel = {
      ...defaultGetOffererResponseModel,
      allowedOnAdage: false,
      managedVenues: [
        {
          ...defaultGetOffererVenueResponseModel,
          collectiveDmsApplications: [
            {
              ...defaultDMSApplicationForEAC,
              application: 1,
              lastChangeDate: '2021-01-01T00:00:00Z',
            },
          ],
        },
      ],
    }
    vi.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
    renderOfferTypes('offererId')

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )

    expect(
      await screen.findByText(
        'Vous avez une demande de référencement en cours de traitement'
      )
    ).toBeInTheDocument()
  })

  it('should display individual offer choices', async () => {
    renderOfferTypes()

    expect(await screen.findByText('Un bien physique')).toBeInTheDocument()
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
      renderOfferTypes()

      await userEvent.click(await screen.findByText(buttonClicked))

      await userEvent.click(
        screen.getByRole('button', { name: 'Étape suivante' })
      )

      expect(screen.getByText('Création individuel')).toBeInTheDocument()
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
    const offersRecap = [collectiveOfferFactory()]
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValueOnce(offersRecap)

    renderOfferTypes()

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )

    await userEvent.click(
      await screen.findByRole('radio', {
        name: 'Une offre réservable Cette offre a une date et un prix. Elle doit être associée à un établissement scolaire avec lequel vous avez préalablement échangé.',
      })
    )

    expect(
      screen.queryByRole('heading', {
        name: 'Créer une nouvelle offre ou dupliquer une offre ?',
      })
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('radio', {
        name: 'Dupliquer les informations d’une offre vitrine Créer une offre réservable en dupliquant les informations d’une offre vitrine existante.',
      })
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    await waitFor(() => {
      expect(api.getCollectiveOffers).toHaveBeenLastCalledWith(
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        undefined,
        'template',
        undefined
      )
    })

    expect(screen.getByText('Sélection collectif')).toBeInTheDocument()
  })

  it('should display error message if trying to duplicate without template offer', async () => {
    const notifyError = vi.fn()
    const notifsImport = (await vi.importActual(
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: notifyError,
    }))

    renderOfferTypes()

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )

    await userEvent.click(
      await screen.findByRole('radio', {
        name: 'Une offre réservable Cette offre a une date et un prix. Elle doit être associée à un établissement scolaire avec lequel vous avez préalablement échangé.',
      })
    )

    await userEvent.click(
      screen.getByRole('radio', {
        name: 'Dupliquer les informations d’une offre vitrine Créer une offre réservable en dupliquant les informations d’une offre vitrine existante.',
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
    renderOfferTypes()

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
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      isValidated: false,
    })
    renderOfferTypes('123')

    expect(
      screen.queryByText(
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
    vi.spyOn(api, 'getOfferer').mockImplementationOnce(() => {
      return new CancelablePromise<GetOffererResponseModel>((resolve) =>
        setTimeout(() => resolve({} as GetOffererResponseModel), 500)
      )
    })

    renderOfferTypes('123')

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )

    expect(await screen.findByText('Chargement en cours')).toBeInTheDocument()
  })
})

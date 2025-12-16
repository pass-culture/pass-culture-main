import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import { api } from '@/apiClient/api'
import type { GetOffererResponseModel } from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import {
  collectiveOfferTemplateFactory,
  defaultDMSApplicationForEAC,
} from '@/commons/utils/factories/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
  getOffererNameFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OfferTypeScreen } from './OfferType'

const mockLogEvent = vi.fn()

vi.mock('@firebase/remote-config', () => ({
  getValue: () => ({ asBoolean: () => true }),
}))

vi.mock('@/apiClient/api', () => ({
  api: {
    listOfferersNames: vi.fn(),
    canOffererCreateEducationalOffer: vi.fn(),
    getCollectiveOfferTemplates: vi.fn(),
    getVenue: vi.fn(),
    getCategories: vi.fn(),
  },
}))

const renderOfferTypes = (
  structureId?: string,
  venueId?: string,
  offerer?: GetOffererResponseModel
) => {
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
        path="/offre/individuelle/creation/details"
        element={<div>Création individuel</div>}
      />
      <Route
        path="/offre/creation/collectif/selection"
        element={<div>Sélection collectif</div>}
      />
    </Routes>,
    {
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
          selectedVenue: makeVenueListItem({ id: 2 }),
        },
        offerer: {
          currentOfferer: {
            ...defaultGetOffererResponseModel,
            isValidated: true,
            ...offerer,
          },
        },
      },
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
    vi.spyOn(api, 'getCollectiveOfferTemplates').mockResolvedValue([])

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should render the component with button', () => {
    renderOfferTypes()

    expect(
      screen.getByRole('radio', { name: /Une offre réservable/ })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('radio', { name: /Une offre vitrine/ })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('radio', { name: /Créer une nouvelle offre/ })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('radio', {
        name: /Dupliquer les informations d’une offre vitrine/,
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Annuler et quitter' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Étape suivante' })
    ).toBeInTheDocument()
  })

  it('should select collective offer', async () => {
    renderOfferTypes()

    expect(
      await screen.findByRole('heading', {
        name: 'Quel est le type de l’offre ?',
      })
    ).toBeInTheDocument()

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
      await screen.findByRole('heading', {
        name: 'Quel est le type de l’offre ?',
      })
    ).toBeInTheDocument()

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

    renderOfferTypes('offererId', 'venueId', offerer)

    expect(
      await screen.findByText(
        'Votre demande est actuellement en cours de traitement.'
      )
    ).toBeInTheDocument()
  })

  it('should select duplicate template offer', async () => {
    const offersRecap = [collectiveOfferTemplateFactory()]
    vi.spyOn(api, 'getCollectiveOfferTemplates').mockResolvedValueOnce(
      offersRecap
    )

    renderOfferTypes()

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
      expect(api.getCollectiveOfferTemplates).toHaveBeenLastCalledWith(
        null,
        1,
        null,
        null,
        null,
        null,
        null,
        null,
        null
      )
    })

    expect(screen.getByText('Sélection collectif')).toBeInTheDocument()
  })

  it('should display error message if trying to duplicate without template offer', async () => {
    const snackBarError = vi.fn()
    const snackBarsImport = (await vi.importActual(
      '@/commons/hooks/useSnackBar'
    )) as ReturnType<typeof useSnackBar.useSnackBar>
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      ...snackBarsImport,
      error: snackBarError,
    }))

    renderOfferTypes()

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

    expect(snackBarError).toHaveBeenCalledWith(
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
    const offerer = {
      ...defaultGetOffererResponseModel,
      isValidated: false,
    }

    renderOfferTypes('123', 'venueId', offerer)

    expect(
      await screen.findByText(
        'Votre structure est actuellement en cours de validation par nos équipes.'
      )
    ).toBeInTheDocument()
  })

  it('should display DS banner if structure not allowed on adage and last ds reference request not found ', async () => {
    const offerer = {
      ...defaultGetOffererResponseModel,
      allowedOnAdage: false,
    }

    renderOfferTypes('123', 'venueId', offerer)

    expect(
      await screen.findByText('Faire une demande de référencement')
    ).toBeInTheDocument()
  })
})

import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  CancelablePromise,
  GetOffererResponseModel,
  SubcategoryIdEnum,
  VenueTypeCode,
} from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import * as useNotification from 'hooks/useNotification'
import {
  collectiveOfferFactory,
  defaultGetOffererVenueResponseModel,
  defautGetOffererResponseModel,
} from 'utils/apiFactories'
import { defaultCollectiveDmsApplication } from 'utils/collectiveApiFactories'
import {
  individualOfferCategoryFactory,
  individualOfferSubCategoryResponseModelFactory,
  individualOfferVenueResponseModelFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferType from '../OfferType'

const mockLogEvent = vi.fn()

vi.mock('hooks/useRemoteConfig', () => ({
  __esModule: true,
  default: () => ({
    remoteConfig: {},
  }),
}))

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

const renderOfferTypes = async (
  storeOverrides: any,
  structureId?: string,
  venueId?: string
) => {
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
        `/creation${
          structureId
            ? `?structure=${structureId}${venueId ? `&lieu=${venueId}` : ''}`
            : ''
        }`,
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

describe.skip('screens:IndividualOffer::OfferType', () => {
  let store: any
  beforeEach(() => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [{ id: 1, name: 'Ma super structure' }],
    })
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue([])
    vi.spyOn(api, 'canOffererCreateEducationalOffer').mockResolvedValue()

    store = {
      user: {
        initialized: true,
        currentUser: {
          isAdmin: false,
          email: 'email@example.com',
        },
      },
      features: {
        list: [{ isActive: true, nameKey: 'WIP_CATEGORY_SELECTION' }],
      },
    }

    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
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
      await screen.findByRole('heading', { name: 'Votre offre est :' })
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )
    await userEvent.click(
      screen.getByRole('radio', {
        name: 'Une offre réservable Cette offre a une date et un prix. Elle doit être associée à un établissement scolaire avec lequel vous avez préalablement échangé.',
      })
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(screen.getByText('Création collectif')).toBeInTheDocument()
  })

  it('should select template offer', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValueOnce({
      offerersNames: [
        { id: 1, name: 'Ma super structure' },
        { id: 2, name: 'Ma super structure #2' },
      ],
    })
    renderOfferTypes(store)

    expect(
      await screen.findByRole('heading', { name: 'Votre offre est :' })
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
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [{ id: 1, name: 'Ma super structure' }],
    })
    vi.spyOn(api, 'canOffererCreateEducationalOffer').mockRejectedValue({})
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

  it('should display dms application banner if offerer can not create collective offer but as dms application', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [{ id: 1, name: 'Ma super structure' }],
    })
    const offerer: GetOffererResponseModel = {
      ...defautGetOffererResponseModel,
      managedVenues: [
        {
          ...defaultGetOffererVenueResponseModel,
          collectiveDmsApplications: [
            {
              ...defaultCollectiveDmsApplication,
              application: 1,
              lastChangeDate: '2021-01-01T00:00:00Z',
            },
          ],
        },
      ],
    }
    vi.spyOn(api, 'getOfferer').mockResolvedValue(offerer)
    vi.spyOn(api, 'canOffererCreateEducationalOffer').mockRejectedValue({})
    renderOfferTypes(store, 'offererId')

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )
    expect(api.canOffererCreateEducationalOffer).toHaveBeenCalledTimes(1)

    expect(
      await screen.findByText(
        'Vous avez une demande de référencement en cours de traitement'
      )
    ).toBeInTheDocument()
  })

  it('should display individual offer choices', async () => {
    renderOfferTypes(store)

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
      renderOfferTypes(store)

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
          subcategoryId: '',
          to: 'informations',
          used: 'StickyButtons',
        }
      )
    }
  )

  it('should log and redirect with subcategory when arriving with venue and chosen a subcategory', async () => {
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [individualOfferCategoryFactory()],
      subcategories: [
        individualOfferSubCategoryResponseModelFactory({
          // id should match venueType in venueTypeSubcategoriesMapping
          id: SubcategoryIdEnum.SPECTACLE_REPRESENTATION,
          proLabel: 'Ma sous-catégorie préférée',
        }),
      ],
    })
    vi.spyOn(api, 'getVenue').mockResolvedValue({
      ...individualOfferVenueResponseModelFactory({
        venueTypeCode: 'OTHER' as VenueTypeCode, // cast is needed because VenueTypeCode in apiClient is defined in french, but sent by api in english
      }),
    })

    // there is a venue in url
    renderOfferTypes(store, '1', '1')

    expect(
      await screen.findByText('Quelle est la catégorie de l’offre ?')
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Ma sous-catégorie préférée'))

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
        offerType: '',
        subcategoryId: 'SPECTACLE_REPRESENTATION',
        to: 'informations',
        used: 'StickyButtons',
      }
    )
  })

  it('should select duplicate template offer', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [{ id: 1, name: 'Ma super structure' }],
    })
    vi.spyOn(api, 'canOffererCreateEducationalOffer').mockResolvedValue()
    const offersRecap = [collectiveOfferFactory()]
    vi.spyOn(api, 'getCollectiveOffers')
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
        name: 'Dupliquer les informations d’une d’offre vitrine Créez une offre réservable en dupliquant les informations d’une offre vitrine existante.',
      })
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(screen.getByText('Sélection collectif')).toBeInTheDocument()
  })

  it('should display error message if trying to duplicate without template offer', async () => {
    vi.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [{ id: 1, name: 'Ma super structure' }],
    })
    vi.spyOn(api, 'canOffererCreateEducationalOffer').mockResolvedValue()
    vi.spyOn(api, 'getCollectiveOffers').mockResolvedValue([])
    const notifyError = vi.fn()
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...vi.importActual('hooks/useNotification'),
      error: notifyError,
    }))

    renderOfferTypes(store)

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )

    await userEvent.click(
      screen.getByRole('radio', {
        name: 'Une offre réservable Cette offre a une date et un prix. Elle doit être associée à un établissement scolaire avec lequel vous avez préalablement échangé.',
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
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
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
    vi.spyOn(api, 'getOfferer').mockImplementationOnce(() => {
      return new CancelablePromise<GetOffererResponseModel>(resolve =>
        setTimeout(() => resolve({} as GetOffererResponseModel), 500)
      )
    })

    renderOfferTypes(store, '123')

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )

    expect(await screen.findByText('Chargement en cours')).toBeInTheDocument()
  })
})

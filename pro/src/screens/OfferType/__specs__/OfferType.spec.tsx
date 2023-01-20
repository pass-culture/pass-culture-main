import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { api } from 'apiClient/api'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
import { configureTestStore } from 'store/testUtils'
import { collectiveOfferFactory } from 'utils/apiFactories'

import OfferType from '../OfferType'

const renderOfferTypes = (storeOverride: any) => {
  const store = configureTestStore(storeOverride)
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={['/creation']}>
        <OfferType />
      </MemoryRouter>
    </Provider>
  )
}

const mockHistoryPush = jest.fn()
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useHistory: () => ({
    push: mockHistoryPush,
  }),
}))

jest.mock('apiClient/api', () => ({
  api: {
    listOfferersNames: jest.fn(),
    canOffererCreateEducationalOffer: jest.fn(),
    getCollectiveOffers: jest.fn(),
  },
}))

jest.mock('hooks/useActiveFeature', () => ({
  __esModule: true,
  default: jest.fn().mockReturnValue(true),
}))

describe('screens:OfferIndividual::OfferType', () => {
  let store: any

  beforeEach(() => {
    store = {
      user: {
        initialized: true,
        currentUser: {
          publicName: 'John Do',
          isAdmin: false,
          email: 'email@example.com',
        },
      },
    }
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

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(mockHistoryPush).toHaveBeenCalledWith({
      pathname: getOfferIndividualPath({
        step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        mode: OFFER_WIZARD_MODE.CREATION,
        isCreation: true,
      }),
      search: '?offer-type=PHYSICAL_GOOD',
    })
  })

  it('should select collective offer', async () => {
    jest.spyOn(api, 'listOfferersNames').mockResolvedValue({
      offerersNames: [
        { id: 'A1', nonHumanizedId: 1, name: 'Ma super structure' },
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
        name: 'Une offre réservable Cette offre a une date et un prix. Vous pouvez choisir de la rendre visible par tous les établissements scolaires ou par un seul.',
      })
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(mockHistoryPush).toHaveBeenCalledWith({
      pathname: '/offre/creation/collectif',
      search: '',
    })
  })

  it('should select template offer', async () => {
    jest.spyOn(api, 'listOfferersNames').mockResolvedValue({
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
    expect(api.canOffererCreateEducationalOffer).toHaveBeenCalledTimes(1)

    await userEvent.click(
      screen.getByRole('radio', {
        name: 'Une offre vitrine Cette offre n’est pas réservable. Elle n’a ni date, ni prix et permet aux enseignants de vous contacter pour co-construire une offre adaptée.',
      })
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(mockHistoryPush).toHaveBeenCalledWith({
      pathname: '/offre/creation/collectif/vitrine',
      search: '',
    })
  })

  it('should display non eligible banner if offerer can not create collective offer', async () => {
    store = {
      ...store,
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
    expect(screen.getByText('Un évènement physique')).toBeInTheDocument()
    expect(screen.getByText('Un évènement numérique')).toBeInTheDocument()
  })

  const individualChoices = [
    {
      buttonClicked: 'Un bien physique',
      expectedSearch: '?offer-type=PHYSICAL_GOOD',
    },
    {
      buttonClicked: 'Un bien numérique',
      expectedSearch: '?offer-type=VIRTUAL_GOOD',
    },
    {
      buttonClicked: 'Un évènement physique',
      expectedSearch: '?offer-type=PHYSICAL_EVENT',
    },
    {
      buttonClicked: 'Un évènement physique',
      expectedSearch: '?offer-type=PHYSICAL_EVENT',
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

      expect(mockHistoryPush).toHaveBeenCalledWith({
        pathname: '/offre/individuelle/creation/informations',
        search: expectedSearch,
      })
    }
  )

  it('should select virtual good', async () => {
    renderOfferTypes(store)

    await userEvent.click(screen.getByText('Un bien numérique'))

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(mockHistoryPush).toHaveBeenCalledWith({
      pathname: '/offre/individuelle/creation/informations',
      search: '?offer-type=VIRTUAL_GOOD',
    })
  })

  it('should select physical event', async () => {
    renderOfferTypes(store)

    await userEvent.click(screen.getByText('Un évènement physique'))

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(mockHistoryPush).toHaveBeenCalledWith({
      pathname: '/offre/individuelle/creation/informations',
      search: '?offer-type=PHYSICAL_EVENT',
    })
  })

  it('should select physical good', async () => {
    renderOfferTypes(store)

    await userEvent.click(screen.getByText('Un évènement numérique'))

    await userEvent.click(
      screen.getByRole('button', { name: 'Étape suivante' })
    )

    expect(mockHistoryPush).toHaveBeenCalledWith({
      pathname: '/offre/individuelle/creation/informations',
      search: '?offer-type=VIRTUAL_EVENT',
    })
  })

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

    expect(mockHistoryPush).toHaveBeenCalledWith({
      pathname: '/offre/creation/collectif/selection',
      search: '',
    })
  })
})

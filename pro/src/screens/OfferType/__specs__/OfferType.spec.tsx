import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { configureTestStore } from 'store/testUtils'

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
      features: {
        list: [
          {
            nameKey: 'OFFER_FORM_V3',
            isActive: false,
          },
          {
            nameKey: 'WIP_CHOOSE_COLLECTIVE_OFFER_TYPE_AT_CREATION',
            isActive: false,
          },
        ],
        initialized: true,
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
    expect(screen.getByRole('link', { name: 'Retour' })).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Étape suivante' })
    ).toBeInTheDocument()
  })

  it('should render new buttons when FF OFFER_FORM_V3 is active ', async () => {
    store.features.list[0].isActive = true

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
      pathname: '/offre/v3/creation/individuelle/informations',
      search: '',
    })
  })

  it('should select collective offer', async () => {
    store.features.list[1].isActive = true

    renderOfferTypes(store)

    expect(
      screen.queryByRole('heading', { name: 'Quel est le type de l’offre ?' })
    ).not.toBeInTheDocument()

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
    store.features.list[1].isActive = true

    renderOfferTypes(store)

    expect(
      screen.queryByRole('heading', { name: 'Quel est le type de l’offre ?' })
    ).not.toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('radio', { name: 'À un groupe scolaire' })
    )
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
})

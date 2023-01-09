import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualPath } from 'core/Offers/utils/getOfferIndividualUrl'
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
      search: '',
    })
  })

  it('should select collective offer', async () => {
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

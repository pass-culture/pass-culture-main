import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route } from 'react-router'

import { configureTestStore } from 'store/testUtils'

import DuplicateOfferCell from '../DuplicateOfferCell'

const LOCAL_STORAGE_HAS_SEEN_MODAL_KEY = 'DUPLICATE_OFFER_MODAL_SEEN'

const renderDuplicateOfferCell = () => {
  const store = configureTestStore({
    user: {
      initialized: true,
      currentUser: {
        publicName: 'John Do',
        isAdmin: false,
        email: 'email@example.com',
      },
    },
  })
  render(
    <Provider store={store}>
      <MemoryRouter initialEntries={['/offres']}>
        <Route path="/offres">
          <table>
            <tbody>
              <tr>
                <DuplicateOfferCell
                  isTemplate
                  templateOfferId="AE"
                ></DuplicateOfferCell>
              </tr>
            </tbody>
          </table>
        </Route>
        <Route path="/offre/duplication/collectif/AE">
          <div>Parcours de duplication d'offre</div>
        </Route>
      </MemoryRouter>
    </Provider>
  )
}

describe('DuplicateOfferCell', () => {
  it('should close dialog when click on cancel button', async () => {
    localStorage.setItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY, 'false')
    renderDuplicateOfferCell()
    const button = screen.getByRole('button', {
      name: 'Créer une offre réservable pour un établissement',
    })

    await userEvent.click(button)

    const modalCancelButton = screen.getByRole('button', {
      name: 'Annuler',
    })
    await userEvent.click(modalCancelButton)

    expect(
      screen.queryByText(
        'Créer une offre réservable pour un établissement scolaire'
      )
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText("Parcours de duplication d'offre")
    ).not.toBeInTheDocument()
  })

  it('should update local storage if user check option to not display modal again ', async () => {
    localStorage.setItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY, 'false')
    renderDuplicateOfferCell()
    const button = screen.getByRole('button', {
      name: 'Créer une offre réservable pour un établissement',
    })

    await userEvent.click(button)

    const checkBox = screen.getByRole('checkbox', {
      name: 'Je ne souhaite plus voir cette information',
    })
    await userEvent.click(checkBox)

    const modalConfirmButton = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })
    await userEvent.click(modalConfirmButton)
    expect(
      screen.getByText("Parcours de duplication d'offre")
    ).toBeInTheDocument()
    expect(localStorage.getItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY)).toEqual(
      'true'
    )
  })

  it('should redirect to offer duplication if user has check option to not display modal again', async () => {
    localStorage.setItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY, 'true')
    renderDuplicateOfferCell()
    const button = screen.getByRole('button', {
      name: 'Créer une offre réservable pour un établissement',
    })

    await userEvent.click(button)

    expect(
      screen.getByText("Parcours de duplication d'offre")
    ).toBeInTheDocument()
  })
})

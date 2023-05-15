import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import * as createFromTemplateUtils from 'core/OfferEducational/utils/createOfferFromTemplate'
import { renderWithProviders } from 'utils/renderWithProviders'

import DuplicateOfferCell, {
  LOCAL_STORAGE_HAS_SEEN_MODAL_KEY,
} from '../DuplicateOfferCell'

jest.mock('core/OfferEducational/utils/createOfferFromTemplate', () => ({
  createOfferFromTemplate: jest.fn(),
}))

const offerId = 12

const renderDuplicateOfferCell = () => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        email: 'email@example.com',
      },
    },
  }

  renderWithProviders(
    <Routes>
      <Route
        path="/offres"
        element={
          <table>
            <tbody>
              <tr>
                <td>
                  <DuplicateOfferCell templateOfferId={offerId} />
                </td>
              </tr>
            </tbody>
          </table>
        }
      />
      <Route
        path={`/offre/duplication/collectif/${offerId}`}
        element={<div>Parcours de duplication d’offre</div>}
      />
    </Routes>,
    { storeOverrides, initialRouterEntries: ['/offres'] }
  )
}

describe('DuplicateOfferCell', () => {
  it('should close dialog when click on cancel button', async () => {
    localStorage.setItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY, 'false')
    renderDuplicateOfferCell()
    const button = screen.getByRole('button', {
      name: 'Dupliquer',
    })

    await userEvent.click(button)

    const modalCancelButton = screen.getByRole('button', {
      name: 'Annuler',
    })
    jest.spyOn(createFromTemplateUtils, 'createOfferFromTemplate')

    await userEvent.click(modalCancelButton)

    expect(
      createFromTemplateUtils.createOfferFromTemplate
    ).not.toHaveBeenCalled()
    expect(screen.queryByLabelText('Dupliquer')).not.toBeInTheDocument()
  })

  it('should update local storage if user check option to not display modal again ', async () => {
    localStorage.setItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY, 'false')
    renderDuplicateOfferCell()
    const button = screen.getByRole('button', {
      name: 'Dupliquer',
    })

    await userEvent.click(button)

    const checkBox = screen.getByRole('checkbox', {
      name: 'Je ne souhaite plus voir cette information',
    })
    await userEvent.click(checkBox)

    const modalConfirmButton = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })
    jest.spyOn(createFromTemplateUtils, 'createOfferFromTemplate')

    await userEvent.click(modalConfirmButton)

    expect(createFromTemplateUtils.createOfferFromTemplate).toHaveBeenCalled()
    expect(localStorage.getItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY)).toEqual(
      'true'
    )
  })

  it('should not update local storage if user does not check any option', async () => {
    localStorage.setItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY, 'false')
    renderDuplicateOfferCell()
    const button = screen.getByRole('button', {
      name: 'Dupliquer',
    })
    await userEvent.click(button)

    const modalConfirmButton = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })
    jest.spyOn(createFromTemplateUtils, 'createOfferFromTemplate')

    await userEvent.click(modalConfirmButton)

    expect(createFromTemplateUtils.createOfferFromTemplate).toHaveBeenCalled()
    expect(localStorage.getItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY)).toEqual(
      'false'
    )
  })

  it('should redirect to offer duplication if user has already check option to not display modal again', async () => {
    localStorage.setItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY, 'true')
    renderDuplicateOfferCell()
    const button = screen.getByRole('button', {
      name: 'Dupliquer',
    })

    jest.spyOn(createFromTemplateUtils, 'createOfferFromTemplate')

    await userEvent.click(button)

    expect(createFromTemplateUtils.createOfferFromTemplate).toHaveBeenCalled()
  })
})

import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fetchMock from 'jest-fetch-mock'
import React from 'react'
import { Route, Routes } from 'react-router-dom'
import * as router from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  ApiError,
  AttachImageResponseModel,
  GetVenueResponseModel,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { CollectiveOffer } from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import * as createFromTemplateUtils from 'core/OfferEducational/utils/createOfferFromTemplate'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import * as useNotification from 'hooks/useNotification'
import * as pcapi from 'repository/pcapi/pcapi'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import DuplicateOfferCell, {
  LOCAL_STORAGE_HAS_SEEN_MODAL_KEY,
} from '../DuplicateOfferCell'

jest.mock('core/OfferEducational/utils/createOfferFromTemplate', () => ({
  createOfferFromTemplate: jest.fn(),
}))

const offerId = 1
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
}))

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
                  <DuplicateOfferCell offerId={offerId} isShowcase={true} />
                </td>
              </tr>
              <tr>
                <td>
                  <DuplicateOfferCell offerId={2} isShowcase={false} />
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
      name: 'Créer une offre réservable',
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
      name: 'Créer une offre réservable',
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
      name: 'Créer une offre réservable',
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
      name: 'Créer une offre réservable',
    })

    jest.spyOn(createFromTemplateUtils, 'createOfferFromTemplate')

    await userEvent.click(button)

    expect(createFromTemplateUtils.createOfferFromTemplate).toHaveBeenCalled()
  })

  describe('DuplicateOfferCell bookable offer', () => {
    let offer: CollectiveOffer
    let offerDuplicate: CollectiveOffer
    const mockNavigate = jest.fn()
    const notifyError = jest.fn()

    beforeEach(() => {
      offer = collectiveOfferFactory()
      offerDuplicate = collectiveOfferFactory()

      jest.spyOn(useNotification, 'default').mockImplementation(() => ({
        ...jest.requireActual('hooks/useNotification'),
        error: notifyError,
      }))

      jest.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)

      jest.spyOn(api, 'getVenue').mockResolvedValue({} as GetVenueResponseModel)

      jest
        .spyOn(api, 'getCategories')
        .mockResolvedValue({ categories: [], subcategories: [] })

      jest
        .spyOn(api, 'listEducationalOfferers')
        .mockResolvedValue({ educationalOfferers: [] })

      jest.spyOn(api, 'listEducationalDomains').mockResolvedValue([])

      jest
        .spyOn(api, 'duplicateCollectiveOffer')
        .mockResolvedValue(offerDuplicate)

      jest
        .spyOn(pcapi, 'postCollectiveOfferImage')
        .mockResolvedValue({} as AttachImageResponseModel)

      fetchMock.mockIf(/image.jpg/, 'some response')
    })

    it('should duplicate bookable offer', async () => {
      jest.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(offer)

      renderDuplicateOfferCell()

      const button = screen.getByRole('button', {
        name: 'Dupliquer',
      })

      await userEvent.click(button)

      expect(api.duplicateCollectiveOffer).toHaveBeenCalledTimes(1)

      expect(mockNavigate).toHaveBeenCalledWith(
        `/offre/collectif/${offerDuplicate.nonHumanizedId}/creation?structure=${offer.venue.managingOfferer.nonHumanizedId}`
      )
    })

    it('should return an error when the collective offer could not be retrieved', async () => {
      jest.spyOn(api, 'getCollectiveOffer').mockRejectedValueOnce('')

      renderDuplicateOfferCell()

      const button = screen.getByRole('button', {
        name: 'Dupliquer',
      })

      await userEvent.click(button)

      const response = await getCollectiveOfferAdapter(offer.nonHumanizedId)

      expect(response.isOk).toBeFalsy()

      expect(notifyError).toHaveBeenNthCalledWith(
        1,
        'Une erreur est survenue lors de la récupération de votre offre'
      )
    })

    it('should return an error when the duplicate collective offer could not be posted', async () => {
      jest.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(offer)
      jest
        .spyOn(api, 'duplicateCollectiveOffer')
        .mockRejectedValueOnce({ status: 500 })

      renderDuplicateOfferCell()

      const button = screen.getByRole('button', {
        name: 'Dupliquer',
      })

      await userEvent.click(button)

      expect(notifyError).toHaveBeenCalledWith(
        'Une erreur est survenue lors de la création de votre offre'
      )
    })

    it('should return an error 400 when the duplicate collective offer could not be posted', async () => {
      jest.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(offer)
      jest
        .spyOn(api, 'duplicateCollectiveOffer')
        .mockRejectedValueOnce(
          new ApiError(
            {} as ApiRequestOptions,
            { status: 400 } as ApiResult,
            ''
          )
        )

      renderDuplicateOfferCell()

      const button = screen.getByRole('button', {
        name: 'Dupliquer',
      })

      await userEvent.click(button)

      expect(notifyError).toHaveBeenCalledWith(
        'Une ou plusieurs erreurs sont présentes dans le formulaire'
      )
    })

    it('should return an error when the categorie call failed', async () => {
      jest.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(offer)

      jest.spyOn(api, 'getCategories').mockRejectedValueOnce('')

      renderDuplicateOfferCell()

      const button = screen.getByRole('button', {
        name: 'Dupliquer',
      })

      await userEvent.click(button)

      expect(notifyError).toHaveBeenNthCalledWith(1, GET_DATA_ERROR_MESSAGE)
    })
  })
})

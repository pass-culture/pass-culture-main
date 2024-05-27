import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import * as router from 'react-router-dom'
import { Route, Routes } from 'react-router-dom'
import createFetchMock from 'vitest-fetch-mock'

import { api } from 'apiClient/api'
import { ApiError, GetCollectiveOfferResponseModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import * as createFromTemplateUtils from 'core/OfferEducational/utils/createOfferFromTemplate'
import * as useNotification from 'hooks/useNotification'
import {
  defaultGetVenue,
  getCollectiveOfferFactory,
} from 'utils/collectiveApiFactories'
import * as localStorageAvailable from 'utils/localStorageAvailable'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import {
  DuplicateOfferCell,
  LOCAL_STORAGE_HAS_SEEN_MODAL_KEY,
} from '../DuplicateOfferCell'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

vi.mock('core/OfferEducational/utils/createOfferFromTemplate', () => ({
  createOfferFromTemplate: vi.fn(),
}))

const offerId = 1
vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useNavigate: vi.fn(),
}))

const renderDuplicateOfferCell = () => {
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
    { user: sharedCurrentUserFactory(), initialRouterEntries: ['/offres'] }
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
    vi.spyOn(createFromTemplateUtils, 'createOfferFromTemplate')

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
    vi.spyOn(createFromTemplateUtils, 'createOfferFromTemplate')

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
    vi.spyOn(createFromTemplateUtils, 'createOfferFromTemplate')

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

    vi.spyOn(createFromTemplateUtils, 'createOfferFromTemplate')

    await userEvent.click(button)

    expect(createFromTemplateUtils.createOfferFromTemplate).toHaveBeenCalled()
  })

  describe('DuplicateOfferCell bookable offer', () => {
    let offer: GetCollectiveOfferResponseModel
    let offerDuplicate: GetCollectiveOfferResponseModel
    const mockNavigate = vi.fn()
    const notifyError = vi.fn()

    beforeEach(async () => {
      offer = getCollectiveOfferFactory()
      offerDuplicate = getCollectiveOfferFactory()

      const notifsImport = (await vi.importActual(
        'hooks/useNotification'
      )) as ReturnType<typeof useNotification.default>
      vi.spyOn(useNotification, 'default').mockImplementation(() => ({
        ...notifsImport,
        error: notifyError,
      }))

      vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)

      vi.spyOn(api, 'getVenue').mockResolvedValue({
        ...defaultGetVenue,
      })

      vi.spyOn(api, 'getNationalPrograms').mockResolvedValue([])

      vi.spyOn(api, 'listEducationalOfferers').mockResolvedValue({
        educationalOfferers: [],
      })

      vi.spyOn(api, 'listEducationalDomains').mockResolvedValue([])

      vi.spyOn(api, 'duplicateCollectiveOffer').mockResolvedValue(
        offerDuplicate
      )

      vi.spyOn(api, 'attachOfferImage').mockResolvedValue({
        imageUrl: 'image.jpg',
      })

      fetchMock.mockIf(/image.jpg/, 'some response')
    })

    it('should duplicate bookable offer', async () => {
      vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(offer)

      renderDuplicateOfferCell()

      const button = screen.getByRole('button', {
        name: 'Dupliquer',
      })

      await userEvent.click(button)

      expect(api.duplicateCollectiveOffer).toHaveBeenCalledTimes(1)

      expect(mockNavigate).toHaveBeenCalledWith(
        `/offre/collectif/${offerDuplicate.id}/creation?structure=${offer.venue.managingOfferer.id}`
      )
    })

    it('should return an error when the collective offer could not be retrieved', async () => {
      vi.spyOn(api, 'getCollectiveOffer').mockRejectedValueOnce('')

      renderDuplicateOfferCell()

      const button = screen.getByRole('button', {
        name: 'Dupliquer',
      })

      await userEvent.click(button)

      expect(notifyError).toHaveBeenCalledWith(
        'Une erreur est survenue lors de la récupération de votre offre'
      )
    })

    it('should return an error when the duplicate collective offer could not be posted', async () => {
      vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(offer)
      vi.spyOn(api, 'duplicateCollectiveOffer').mockRejectedValueOnce({
        status: 500,
      })

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
      vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(offer)
      vi.spyOn(api, 'duplicateCollectiveOffer').mockRejectedValueOnce(
        new ApiError({} as ApiRequestOptions, { status: 400 } as ApiResult, '')
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
  })

  it('should not display the modal if the localstorage is not available', async () => {
    localStorage.setItem(LOCAL_STORAGE_HAS_SEEN_MODAL_KEY, 'true')

    renderDuplicateOfferCell()

    vi.spyOn(
      localStorageAvailable,
      'localStorageAvailable'
    ).mockImplementationOnce(() => false)

    const button = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })

    await userEvent.click(button)

    expect(
      screen.getByText(
        'Créer une offre réservable pour un établissement scolaire'
      )
    ).toBeInTheDocument()
  })
})

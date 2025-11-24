import { screen } from '@testing-library/react'
import * as router from 'react-router'
import { expect } from 'vitest'

import type {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import {
  defaultAdageUser,
  defaultCollectiveOffer,
  defaultCollectiveTemplateOffer,
} from '@/commons/utils/factories/adageFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { AdageUserContextProvider } from '@/pages/AdageIframe/app/providers/AdageUserContext'

import { AdageOffer } from '../AdageOffer'

const defaultUseLocationValue = {
  state: { offer: defaultCollectiveTemplateOffer, queryId: '' },
  hash: '',
  key: '',
  pathname: '/adage-iframe/recherche',
  search: '',
}

function renderAdageOffer({
  offer,
  isPreview = false,
  playlistId,
}: {
  offer: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
  isPreview?: boolean
  playlistId?: number
}) {
  return renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <AdageOffer
        offer={offer}
        adageUser={defaultAdageUser}
        isPreview={isPreview}
        playlistId={playlistId}
      />
    </AdageUserContextProvider>
  )
}

vi.mock('@/apiClient/api', () => ({
  apiAdage: {
    logConsultOffer: vi.fn(),
  },
}))

describe('AdageOffer', () => {
  it('should display the offer information sections', () => {
    renderAdageOffer({ offer: defaultCollectiveTemplateOffer })

    expect(
      screen.getByRole('heading', { name: 'Détails de l’offre' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Informations pratiques' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Public concerné' })
    ).toBeInTheDocument()
  })

  it('should show the offer cultural partner infos for a collective offer', () => {
    renderAdageOffer({ offer: defaultCollectiveTemplateOffer })

    expect(
      screen.getByRole('heading', { name: 'Partenaire culturel' })
    ).toBeInTheDocument()
  })

  it('should show the offer instistution panel for a collective bookable offer', () => {
    renderAdageOffer({ offer: defaultCollectiveOffer })

    expect(
      screen.getByRole('heading', { name: 'Offre adressée à :' })
    ).toBeInTheDocument()
  })

  it('should call tracker when coming from search page', () => {
    vi.spyOn(router, 'useLocation').mockReturnValueOnce({
      ...defaultUseLocationValue,
      state: { queryId: 123 },
    })

    renderAdageOffer({ offer: defaultCollectiveOffer })

    expect(apiAdage.logConsultOffer).toHaveBeenCalledWith(
      expect.objectContaining({
        iframeFrom: '/adage-iframe/recherche',
        offerId: defaultCollectiveOffer.id,
        queryId: 123,
      })
    )
  })

  it('should call tracker with source when coming from a shareLink', () => {
    vi.spyOn(router, 'useLocation').mockReturnValueOnce({
      ...defaultUseLocationValue,
      search: '?source=shareLink',
    })

    renderAdageOffer({ offer: defaultCollectiveOffer })

    expect(apiAdage.logConsultOffer).toHaveBeenCalledWith(
      expect.objectContaining({
        iframeFrom: '/adage-iframe/recherche',
        offerId: defaultCollectiveOffer.id,
        source: 'shareLink',
      })
    )
  })

  it('should call tracker with playlistId when coming from a discovery', () => {
    vi.spyOn(router, 'useLocation').mockReturnValueOnce(defaultUseLocationValue)

    renderAdageOffer({
      offer: defaultCollectiveOffer,
      playlistId: 42,
    })

    expect(apiAdage.logConsultOffer).toHaveBeenCalledWith(
      expect.objectContaining({
        iframeFrom: '/adage-iframe/recherche',
        offerId: defaultCollectiveOffer.id,
        playlistId: 42,
      })
    )
  })
})

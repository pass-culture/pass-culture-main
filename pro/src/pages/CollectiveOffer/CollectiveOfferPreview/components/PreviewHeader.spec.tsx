import { screen } from '@testing-library/react'
import { expect } from 'vitest'

import { CollectiveOfferDisplayedStatus } from '@/apiClient//v1'
import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { PreviewHeader } from './PreviewHeader'

describe('PreviewHeader', () => {
  const baseOffer = getCollectiveOfferFactory()

  const renderPreviewHeader = (
    displayedStatus: CollectiveOfferDisplayedStatus = CollectiveOfferDisplayedStatus.UNDER_REVIEW
  ) => {
    renderWithProviders(
      <PreviewHeader
        offer={{
          ...baseOffer,
          displayedStatus,
        }}
      />
    )
  }

  it('should show the preview explanation paragraph', () => {
    renderPreviewHeader()

    expect(
      screen.getByText(
        'Voici un aperçu de votre offre à destination de l’établissement scolaire sur la plateforme ADAGE.'
      )
    ).toBeInTheDocument()
  })

  it('should not show the not visible preview callout when the status is not in statusLabel', () => {
    renderPreviewHeader(CollectiveOfferDisplayedStatus.PUBLISHED)
    expect(
      screen.queryByText(/Cet aperçu n’est pas visible par l’enseignant/)
    ).not.toBeInTheDocument()
  })

  it.each([
    [CollectiveOfferDisplayedStatus.UNDER_REVIEW, "en cours d'instruction"],
    [CollectiveOfferDisplayedStatus.REJECTED, 'non conforme'],
    [CollectiveOfferDisplayedStatus.CANCELLED, 'annulée'],
    [CollectiveOfferDisplayedStatus.EXPIRED, 'expirée'],
    [CollectiveOfferDisplayedStatus.ENDED, 'terminée'],
    [CollectiveOfferDisplayedStatus.REIMBURSED, 'terminée'],
    [CollectiveOfferDisplayedStatus.ARCHIVED, 'archivée'],
    [CollectiveOfferDisplayedStatus.HIDDEN, 'en pause'],
  ])(
    'should show not visible preview callout for status %s',
    (status, expectedLabel) => {
      renderPreviewHeader(status)

      expect(
        screen.getByText(
          `Cet aperçu n'est pas visible par l'enseignant car votre offre est ${expectedLabel}.`
        )
      ).toBeInTheDocument()
    }
  )
})

import { screen } from '@testing-library/react'

import { IndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { individualOfferContextValuesFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component as IndividualOfferSummaryMedia } from './IndividualOfferSummaryMedia'

const renderIndividualOfferSummaryScreen = () => {
  const contextValue = individualOfferContextValuesFactory()

  renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <IndividualOfferSummaryMedia />
    </IndividualOfferContext.Provider>
  )
}

const LABELS = {
  mediaSectionTitle: 'Image et vidéo',
  actionBarLinkLabel: 'Retour à la liste des offres',
}

describe('IndividualOfferSummaryMedia', () => {
  it('should render a media section', () => {
    renderIndividualOfferSummaryScreen()

    const mediaSection = screen.getByRole('heading', {
      name: LABELS.mediaSectionTitle,
    })
    expect(mediaSection).toBeInTheDocument()
  })

  it('should render an action bar & back to offers list button', () => {
    renderIndividualOfferSummaryScreen()

    const actionBarLink = screen.getByRole('link', {
      name: LABELS.actionBarLinkLabel,
    })
    expect(actionBarLink).toBeInTheDocument()
  })
})

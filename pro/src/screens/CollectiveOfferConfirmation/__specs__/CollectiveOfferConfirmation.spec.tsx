import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import { OfferStatus } from 'apiClient/v1'

import CollectiveOfferConfirmation from '../CollectiveOfferConfirmation'

describe('CollectiveOfferConfirmation', () => {
  it('should render confirmation page when offer is pending', () => {
    render(
      <Router history={createBrowserHistory()}>
        <CollectiveOfferConfirmation
          offererId="O1"
          offerStatus={OfferStatus.PENDING}
          isShowcase={false}
          institutionDisplayName="Collège Bellevue"
        />
      </Router>
    )

    expect(
      screen.getByText('Offre en cours de validation !')
    ).toBeInTheDocument()
  })

  it('should render confirmation page when offer is active and associated to an institution', () => {
    render(
      <Router history={createBrowserHistory()}>
        <CollectiveOfferConfirmation
          offererId="O1"
          offerStatus={OfferStatus.ACTIVE}
          isShowcase={false}
          institutionDisplayName="Collège Bellevue"
        />
      </Router>
    )

    expect(screen.getByText('Offre créée avec succès !')).toBeInTheDocument()
    expect(
      screen.getByText('Collège Bellevue', { exact: false })
    ).toBeInTheDocument()
  })

  it('should render confirmation page when offer is active and associated to all institutions', () => {
    render(
      <Router history={createBrowserHistory()}>
        <CollectiveOfferConfirmation
          offererId="O1"
          offerStatus={OfferStatus.ACTIVE}
          isShowcase={false}
          institutionDisplayName=""
        />
      </Router>
    )

    expect(screen.getByText('Offre créée avec succès !')).toBeInTheDocument()
    expect(
      screen.getByText('visible par les enseignants et chefs d’établissement', {
        exact: false,
      })
    ).toBeInTheDocument()
  })

  it('should render confirmation page when offer is active and template', () => {
    render(
      <Router history={createBrowserHistory()}>
        <CollectiveOfferConfirmation
          offererId=""
          offerStatus={OfferStatus.ACTIVE}
          isShowcase={true}
          institutionDisplayName=""
        />
      </Router>
    )

    expect(screen.getByText('Offre créée avec succès !')).toBeInTheDocument()
  })
})

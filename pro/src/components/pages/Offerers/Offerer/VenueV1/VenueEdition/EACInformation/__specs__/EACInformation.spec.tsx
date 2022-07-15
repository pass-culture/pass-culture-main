import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'

import EACInformation from '../EACInformation'
import type { History } from 'history'
import React from 'react'
import { Router } from 'react-router-dom'
import { createBrowserHistory } from 'history'

describe('EACInformation', () => {
  let history: History
  beforeAll(() => {
    history = createBrowserHistory()
  })
  it('should display information banner when user is creating venue and can create collective offers', async () => {
    render(
      <Router history={history}>
        <EACInformation
          venue={null}
          isCreatingVenue
          canOffererCreateCollectiveOffer
          offererId="O1"
        />
      </Router>
    )

    expect(
      await screen.findByText(
        'Une fois votre lieu créé, vous pourrez renseigner des informations pour les enseignants en revenant sur cette page.'
      )
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('link', { name: 'Renseigner mes informations' })
    ).toHaveAttribute('aria-disabled')
  })

  it('should display information banner when user is creating venue and cannot create collective offers', async () => {
    render(
      <Router history={history}>
        <EACInformation
          venue={null}
          isCreatingVenue
          canOffererCreateCollectiveOffer={false}
          offererId="O1"
        />
      </Router>
    )

    expect(
      await screen.findByText(
        'Pour proposer des informations à destination d’un groupe scolaire, vous devez être référencé auprès du ministère de l’Éducation Nationale et du ministère de la Culture.'
      )
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('link', { name: 'Renseigner mes informations' })
    ).toHaveAttribute('aria-disabled')
  })
})

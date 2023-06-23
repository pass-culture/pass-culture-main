import { screen } from '@testing-library/react'
import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferConfirmation from '../CollectiveOfferConfirmation'

describe('CollectiveOfferConfirmation', () => {
  it('should render confirmation page when offer is pending', () => {
    renderWithProviders(
      <CollectiveOfferConfirmation
        offererId={1}
        offerStatus={OfferStatus.PENDING}
        isShowcase={false}
        institutionDisplayName="Collège Bellevue"
      />
    )

    expect(
      screen.getByText('Offre en cours de validation !')
    ).toBeInTheDocument()
  })

  it('should render confirmation page when offer is active and associated to an institution', () => {
    renderWithProviders(
      <CollectiveOfferConfirmation
        offererId={1}
        offerStatus={OfferStatus.ACTIVE}
        isShowcase={false}
        institutionDisplayName="Collège Bellevue"
      />
    )

    expect(
      screen.getByText('Votre offre a été publiée sur ADAGE')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Collège Bellevue', { exact: false })
    ).toBeInTheDocument()
  })

  it('should render confirmation page when offer is active and associated to all institutions', () => {
    renderWithProviders(
      <CollectiveOfferConfirmation
        offererId={1}
        offerStatus={OfferStatus.ACTIVE}
        isShowcase={false}
        institutionDisplayName=""
      />
    )

    expect(
      screen.getByText('Votre offre a été publiée sur ADAGE')
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'visible et réservable par les enseignants et chefs d’établissements',
        {
          exact: false,
        }
      )
    ).toBeInTheDocument()
  })

  it('should render confirmation page when offer is active and template', () => {
    renderWithProviders(
      <CollectiveOfferConfirmation
        offererId={null}
        offerStatus={OfferStatus.ACTIVE}
        isShowcase={true}
        institutionDisplayName=""
      />
    )

    expect(
      screen.getByText('Votre offre a été publiée sur ADAGE')
    ).toBeInTheDocument()
  })

  it('should render banner at the bottom of the page', () => {
    renderWithProviders(
      <CollectiveOfferConfirmation
        offererId={null}
        offerStatus={OfferStatus.ACTIVE}
        isShowcase={true}
        institutionDisplayName=""
      />
    )

    expect(
      screen.getByText('Quelle est la prochaine étape ?')
    ).toBeInTheDocument()
  })
})

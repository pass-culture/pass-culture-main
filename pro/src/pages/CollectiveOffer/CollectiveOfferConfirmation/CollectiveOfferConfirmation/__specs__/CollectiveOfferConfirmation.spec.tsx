import { screen } from '@testing-library/react'

import { CollectiveOfferDisplayedStatus } from 'apiClient/v1'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { CollectiveOfferConfirmationScreen } from '../CollectiveOfferConfirmation'

describe('CollectiveOfferConfirmation', () => {
  it('should render confirmation page when offer is pending', () => {
    renderWithProviders(
      <CollectiveOfferConfirmationScreen
        offererId={1}
        offerStatus={CollectiveOfferDisplayedStatus.UNDER_REVIEW}
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
      <CollectiveOfferConfirmationScreen
        offererId={1}
        offerStatus={CollectiveOfferDisplayedStatus.PUBLISHED}
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
      <CollectiveOfferConfirmationScreen
        offererId={1}
        offerStatus={CollectiveOfferDisplayedStatus.PUBLISHED}
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
      <CollectiveOfferConfirmationScreen
        offererId={null}
        offerStatus={CollectiveOfferDisplayedStatus.PUBLISHED}
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
      <CollectiveOfferConfirmationScreen
        offererId={null}
        offerStatus={CollectiveOfferDisplayedStatus.PUBLISHED}
        isShowcase={true}
        institutionDisplayName=""
      />
    )

    expect(
      screen.getByText('Quelle est la prochaine étape ?')
    ).toBeInTheDocument()
  })
})

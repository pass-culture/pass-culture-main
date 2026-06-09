import { screen } from '@testing-library/dom'
import userEvent from '@testing-library/user-event'
import { useParams } from 'react-router'
import { axe } from 'vitest-axe'

import { OfferStatus } from '@/apiClient/v1/new'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOffersCTA } from './IndividualOffersCTA'

const renderIndividualOffersCTA = (
  offerStatus: React.ComponentProps<
    typeof IndividualOffersCTA
  >['offerStatus'] = OfferStatus.PUBLISHED
) => {
  const user = userEvent.setup()
  const props = { offerId: 12, offerStatus }

  const FakeOfferDetailComponent = () => {
    const { offerId } = useParams()
    return <div>Detail de mon offre {offerId}</div>
  }

  const FakeTarifEditionComponent = () => {
    const { offerId } = useParams()
    return <div>Modification du tarif de mon offre {offerId}</div>
  }

  return {
    ...renderWithProviders(null, {
      routes: [
        {
          path: '/',
          element: <IndividualOffersCTA {...props} />,
        },
        {
          path: '/offre/individuelle/:offerId/recapitulatif/description',
          element: <FakeOfferDetailComponent />,
        },
        {
          path: '/offre/individuelle/:offerId/edition/tarifs',
          element: <FakeTarifEditionComponent />,
        },
      ],
    }),
    user,
  }
}

describe('<IndividualOffersCTA />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderIndividualOffersCTA()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render a CTA to change offer tarif if offer is sold out', async () => {
    const { user } = renderIndividualOffersCTA(OfferStatus.SOLD_OUT)
    const cta = screen.getByRole('link', { name: 'Ajouter du stock' })
    expect(cta).toBeVisible()

    await user.click(cta)

    expect(
      screen.getByText('Modification du tarif de mon offre 12')
    ).toBeVisible()
  })

  it('should render a CTA to see offer details otherwise', async () => {
    const { user } = renderIndividualOffersCTA()
    const cta = screen.getByRole('link', { name: "Voir l'offre" })
    expect(cta).toBeVisible()

    await user.click(cta)

    expect(screen.getByText('Detail de mon offre 12')).toBeVisible()
  })
})

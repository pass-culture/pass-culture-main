import { screen } from '@testing-library/dom'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { buildCollectiveOfferTemplateHome } from '@/commons/utils/factories/adageFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOffersTemplateCard } from './CollectiveOffersTemplateCard'
import type { CollectiveOffersTemplateLineProps } from './components/CollectiveOffersTemplateLine/CollectiveOffersTemplateLine'

vi.mock(
  './components/CollectiveOffersTemplateLine/CollectiveOffersTemplateLine',
  () => ({
    CollectiveOffersTemplateLine: ({
      offer,
    }: CollectiveOffersTemplateLineProps) => (
      <div data-testid="collective-offer-template-line">
        Line for offer {offer.id}
      </div>
    ),
  })
)

describe('<CollectiveOffersTemplateCard />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(
      <CollectiveOffersTemplateCard
        offers={[buildCollectiveOfferTemplateHome()]}
      />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render one CollectiveOffersTemplateLine per offer given', () => {
    const offer = buildCollectiveOfferTemplateHome()
    renderWithProviders(
      <CollectiveOffersTemplateCard
        offers={[
          { ...offer, id: 1 },
          { ...offer, id: 2 },
          { ...offer, id: 3 },
        ]}
      />
    )

    const allOfferLines = screen.getAllByTestId(
      'collective-offer-template-line'
    )
    expect(allOfferLines.length).toBe(3)
    allOfferLines.forEach((line, idx) => {
      expect(line).toHaveTextContent(`Line for offer ${idx + 1}`)
    })
  })

  it('should have a CTA that sends to template offer list', async () => {
    const user = userEvent.setup()
    const offer = buildCollectiveOfferTemplateHome()

    renderWithProviders(null, {
      routes: [
        {
          path: '/',
          element: <CollectiveOffersTemplateCard offers={[offer]} />,
        },
        {
          path: '/offres/vitrines',
          element: <div>Liste de toutes les offres vitrines</div>,
        },
      ],
    })

    const allOffersBtn = screen.getByRole('link', {
      name: 'Voir toutes les offres',
    })
    expect(allOffersBtn).toBeVisible()
    await user.click(allOffersBtn)

    expect(
      screen.getByText('Liste de toutes les offres vitrines')
    ).toBeVisible()
  })
})

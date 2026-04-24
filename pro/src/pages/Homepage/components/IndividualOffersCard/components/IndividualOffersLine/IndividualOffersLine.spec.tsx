import { screen } from '@testing-library/dom'
import userEvent from '@testing-library/user-event'
import { useParams } from 'react-router'
import { axe } from 'vitest-axe'

import { type OfferHomeResponseModel, OfferStatus } from '@/apiClient/v1'
import { defaultOfferHomeResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOffersLine } from './IndividualOffersLine'

vi.mock('../IndividualOffersTag/IndividualOffersTag', () => ({
  IndividualOffersTag: () => <div>IndividualOffersTag</div>,
}))

describe('<IndividualOffersLine />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(
      <IndividualOffersLine
        offer={defaultOfferHomeResponseModel}
        venueDepartmentCode={'75'}
      />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display the right content for non expiring offers', () => {
    const offer: OfferHomeResponseModel = {
      ...defaultOfferHomeResponseModel,
      stocks: [{ beginningDatetime: '2026-02-01T10:00:00Z' }],
      departmentCode: null,
    }
    renderWithProviders(
      <IndividualOffersLine offer={offer} venueDepartmentCode={null} />
    )

    expect(screen.getByRole('img')).toBeVisible()
    expect(screen.getByText(offer.name)).toBeVisible()
    expect(screen.getByText('Le 01/02/2026 11:00')).toBeVisible()
    expect(screen.getByText('publiée')).toBeVisible()
    expect(screen.getByRole('link', { name: "Voir l'offre" })).toBeVisible()
    expect(screen.getByText('IndividualOffersTag')).toBeVisible()
  })

  it('should display the right date for offers in Reunion (UTC+4)', () => {
    const offer: OfferHomeResponseModel = {
      ...defaultOfferHomeResponseModel,
      stocks: [{ beginningDatetime: '2026-02-01T10:00:00Z' }],
      departmentCode: '974',
    }
    renderWithProviders(
      <IndividualOffersLine offer={offer} venueDepartmentCode={'75'} />
    )

    expect(screen.getByText('Le 01/02/2026 14:00')).toBeVisible()
  })

  it('should display the right date for offers in Guadeloupe (UTC-4)', () => {
    const offer: OfferHomeResponseModel = {
      ...defaultOfferHomeResponseModel,
      stocks: [{ beginningDatetime: '2026-02-01T10:00:00Z' }],
      departmentCode: '971',
    }
    renderWithProviders(
      <IndividualOffersLine offer={offer} venueDepartmentCode={'75'} />
    )

    expect(screen.getByText('Le 01/02/2026 06:00')).toBeVisible()
  })

  it("should fallback to the venue timezone if offer doesn't have one", () => {
    const offer: OfferHomeResponseModel = {
      ...defaultOfferHomeResponseModel,
      stocks: [{ beginningDatetime: '2026-02-01T10:00:00Z' }],
      departmentCode: null,
    }
    renderWithProviders(
      <IndividualOffersLine offer={offer} venueDepartmentCode={'989'} />
    )

    expect(screen.getByText('Le 01/02/2026 02:00')).toBeVisible()
  })

  it('should display the number of dates if there are several stocks on event offers', () => {
    const offer: OfferHomeResponseModel = {
      ...defaultOfferHomeResponseModel,
      stocks: [
        { beginningDatetime: '2026-02-01T10:00:00Z' },
        { beginningDatetime: '2026-02-02T10:00:00Z' },
      ],
      departmentCode: '971',
    }
    renderWithProviders(
      <IndividualOffersLine offer={offer} venueDepartmentCode={'75'} />
    )

    expect(screen.getByText('2 dates')).toBeVisible()
  })

  it("should not display the date if offer's stock has no date", () => {
    const offer: OfferHomeResponseModel = {
      ...defaultOfferHomeResponseModel,
      stocks: [{ beginningDatetime: null }],
      departmentCode: '971',
    }
    renderWithProviders(
      <IndividualOffersLine offer={offer} venueDepartmentCode={'75'} />
    )

    expect(
      screen.queryByText(/Le \d{2}\/\d{2}\/\d{4} \d{2}:\d{2}/)
    ).not.toBeInTheDocument()
  })

  describe('clickable behaviour', () => {
    const renderIndividualOffersLineWithRouter = (
      offerStatus: OfferStatus = OfferStatus.PUBLISHED
    ) => {
      const user = userEvent.setup()
      const offer: OfferHomeResponseModel = {
        ...defaultOfferHomeResponseModel,
        status: offerStatus,
      }

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
              element: (
                <IndividualOffersLine
                  offer={offer}
                  venueDepartmentCode={'989'}
                />
              ),
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
        offer,
      }
    }

    it('should have the line clickable', async () => {
      const { user, offer } = renderIndividualOffersLineWithRouter()
      expect(screen.getByRole('img')).toBeVisible()

      await user.click(
        screen.getByRole('link', {
          name: `12 réservations - ${offer.name} - Le 15/10/2021 14:00 - publiée`,
        })
      )

      expect(screen.getByText(`Detail de mon offre ${offer.id}`)).toBeVisible()
    })

    it('the CTA should still redirect to its own link', async () => {
      const { user, offer } = renderIndividualOffersLineWithRouter(
        OfferStatus.SOLD_OUT
      )
      expect(screen.getByText(offer.name)).toBeVisible()

      await user.click(screen.getByRole('link', { name: 'Ajouter du stock' }))

      expect(
        screen.getByText(`Modification du tarif de mon offre ${offer.id}`)
      ).toBeVisible()
    })
  })
})

import { render, screen } from '@testing-library/react'

import { CollectiveAdditionalFeeType } from '@/apiClient/v1'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { getCollectiveOfferCollectiveStockFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { TOTAL_PRICE_LABEL } from '@/pages/CollectiveOffer/CollectiveOfferStock/components/OfferEducationalStock/constants/labels'

import {
  CollectiveOfferStockSection,
  type CollectiveOfferStockSectionProps,
} from '../CollectiveOfferStockSection'

vi.mock('@/commons/hooks/useActiveFeature', () => ({
  useActiveFeature: vi.fn(),
}))

const renderCollectiveOfferStockSection = (
  props: CollectiveOfferStockSectionProps
) => {
  return render(<CollectiveOfferStockSection {...props} />)
}

describe('CollectiveOfferStockSection', () => {
  it('render component', () => {
    vi.mocked(useActiveFeature).mockReturnValue(false)

    const props = {
      stock: getCollectiveOfferCollectiveStockFactory(),
    }
    renderCollectiveOfferStockSection(props)

    expect(screen.getByText('Date de début :')).toBeVisible()
    expect(screen.getByText('Date de fin :')).toBeVisible()
    expect(screen.getByText('Horaire :')).toBeVisible()
    expect(screen.getByText('Nombre de participants :')).toBeVisible()
    expect(screen.getByText(`${TOTAL_PRICE_LABEL} :`)).toBeVisible()
    expect(screen.getByText('Informations sur le prix :')).toBeVisible()
    expect(screen.getByText('Date limite de réservation :')).toBeVisible()
  })

  describe('WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS enabled', () => {
    beforeEach(() => {
      vi.mocked(useActiveFeature).mockReturnValue(true)
    })

    it('should display new price subsections', () => {
      const props = {
        stock: getCollectiveOfferCollectiveStockFactory({
          servicePrice: 80,
          price: 145.5,
          numberOfTickets: 25,
          numberOfTeachers: 3,
          collectiveAdditionalFees: [
            {
              type: CollectiveAdditionalFeeType.TRAVEL,
              label: null,
              amount: 65.5,
            },
          ],
        }),
      }
      renderCollectiveOfferStockSection(props)

      expect(screen.getByText('Prix de votre offre')).toBeVisible()

      const servicePriceRow = screen
        .getByText('Tarif de la prestation :')
        .closest('.summary-layout-row')
      expect(servicePriceRow).toHaveTextContent('80€')

      const totalPriceRow = screen
        .getByText('Prix total TTC :')
        .closest('.summary-layout-row')
      expect(totalPriceRow).toHaveTextContent('145.5€')
    })

    it('should display number of students and teachers', () => {
      const props = {
        stock: getCollectiveOfferCollectiveStockFactory({
          numberOfTickets: 25,
          numberOfTeachers: 3,
        }),
      }
      renderCollectiveOfferStockSection(props)

      const studentsRow = screen
        .getByText("Nombre d'élèves :")
        .closest('.summary-layout-row')
      expect(studentsRow).toHaveTextContent('25')

      const teachersRow = screen
        .getByText("Nombre d'accompagnateurs :")
        .closest('.summary-layout-row')
      expect(teachersRow).toHaveTextContent('3')
    })

    it('should display 0 for number of teachers when value is 0', () => {
      const props = {
        stock: getCollectiveOfferCollectiveStockFactory({
          numberOfTeachers: 0,
        }),
      }
      renderCollectiveOfferStockSection(props)

      const teachersRow = screen
        .getByText("Nombre d'accompagnateurs :")
        .closest('.summary-layout-row')
      expect(teachersRow).toHaveTextContent('0')
    })

    it('should display "Non" for additional fees when list is empty', () => {
      const props = {
        stock: getCollectiveOfferCollectiveStockFactory({
          collectiveAdditionalFees: [],
        }),
      }
      renderCollectiveOfferStockSection(props)

      expect(screen.getByText('Frais annexes :')).toBeVisible()
      expect(screen.getByText('Non')).toBeVisible()
      expect(
        screen.queryByText('Type de frais annexe :')
      ).not.toBeInTheDocument()
    })

    it('should display "Oui" and the list of additional fees', () => {
      const props = {
        stock: getCollectiveOfferCollectiveStockFactory({
          collectiveAdditionalFees: [
            {
              type: CollectiveAdditionalFeeType.TRAVEL,
              label: 'Transport en bus',
              amount: 30,
            },
            {
              type: CollectiveAdditionalFeeType.MEAL,
              label: null,
              amount: 12.5,
            },
          ],
        }),
      }
      renderCollectiveOfferStockSection(props)

      expect(screen.getByText('Frais annexes :')).toBeVisible()
      expect(screen.getByText('Oui')).toBeVisible()
      expect(screen.getByText('Type de frais annexe :')).toBeVisible()
      expect(screen.getByText('Transport en bus - 30€')).toBeVisible()
      expect(screen.getByText("Repas de l'intervenant•e - 12.5€")).toBeVisible()
    })
  })
})

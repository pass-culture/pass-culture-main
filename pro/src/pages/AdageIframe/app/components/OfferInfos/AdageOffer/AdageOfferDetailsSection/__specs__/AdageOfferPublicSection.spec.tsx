import { render, screen } from '@testing-library/react'

import { StudentLevels } from '@/apiClient/adage'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import {
  defaultCollectiveOffer,
  defaultCollectiveTemplateOffer,
} from '@/commons/utils/factories/adageFactories'

import {
  AdageOfferPublicSection,
  type AdageOfferPublicSectionProps,
} from '../AdageOfferPublicSection'

vi.mock('@/commons/hooks/useActiveFeature', () => ({
  useActiveFeature: vi.fn(),
}))

function renderAdageOfferPublicSection(
  props: AdageOfferPublicSectionProps = {
    offer: defaultCollectiveTemplateOffer,
  }
) {
  return render(<AdageOfferPublicSection {...props} />)
}

describe('AdageOfferPublicSection', () => {
  beforeEach(() => {
    vi.mocked(useActiveFeature).mockReturnValue(false)
  })
  it('should display the offer students levels', () => {
    renderAdageOfferPublicSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        students: [StudentLevels.COLL_GE_3E, StudentLevels.COLL_GE_6E],
      },
    })

    expect(
      screen.getByRole('heading', { name: 'Niveau scolaire' })
    ).toBeVisible()
    expect(screen.getByText('Collège - 3e')).toBeVisible()
    expect(screen.getByText('Collège - 6e')).toBeVisible()
  })

  it('should not display the students levels section if the offer has no students levels', () => {
    renderAdageOfferPublicSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        students: [],
      },
    })

    expect(
      screen.queryByRole('heading', { name: 'Niveau scolaire' })
    ).not.toBeInTheDocument()
  })

  it('should display the offer accessibility criteria', () => {
    renderAdageOfferPublicSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        audioDisabilityCompliant: true,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        visualDisabilityCompliant: true,
      },
    })

    expect(
      screen.getByRole('heading', {
        name: 'Accessibilité',
      })
    ).toBeVisible()
    expect(screen.getByText('Psychique ou cognitif')).toBeVisible()
    expect(screen.getByText('Auditif')).toBeVisible()
    expect(screen.getByText('Moteur')).toBeVisible()
    expect(screen.getByText('Visuel')).toBeVisible()
  })

  it('should show that the offer is not accessible if the offer has no accessibility criteria enabled', () => {
    renderAdageOfferPublicSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        audioDisabilityCompliant: false,
        mentalDisabilityCompliant: false,
        motorDisabilityCompliant: false,
        visualDisabilityCompliant: false,
      },
    })

    expect(screen.getByText('Non accessible')).toBeVisible()
  })

  describe('WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS', () => {
    beforeEach(() => {
      vi.mocked(useActiveFeature).mockReturnValue(true)
    })

    it('should display the number of participants section for a bookable offer', () => {
      renderAdageOfferPublicSection({
        offer: {
          ...defaultCollectiveOffer,
          stock: {
            ...defaultCollectiveOffer.stock,
            numberOfTickets: 28,
            numberOfTeachers: 2,
          },
        },
      })

      expect(
        screen.getByRole('heading', { name: 'Nombre de participants' })
      ).toBeVisible()
      expect(screen.getByText('28 élèves')).toBeVisible()
      expect(screen.getByText('2 accompagnateurs')).toBeVisible()
    })

    it('should not display accompagnateurs when numberOfTeachers is 0', () => {
      renderAdageOfferPublicSection({
        offer: {
          ...defaultCollectiveOffer,
          stock: {
            ...defaultCollectiveOffer.stock,
            numberOfTickets: 28,
            numberOfTeachers: 0,
          },
        },
      })

      expect(screen.getByText('28 élèves')).toBeVisible()
      expect(screen.queryByText(/accompagnateur/)).not.toBeInTheDocument()
    })

    it('should not display the number of participants section for a template offer', () => {
      renderAdageOfferPublicSection({
        offer: defaultCollectiveTemplateOffer,
      })

      expect(
        screen.queryByRole('heading', { name: 'Nombre de participants' })
      ).not.toBeInTheDocument()
    })
  })
})

import { render, screen } from '@testing-library/react'

import { StudentLevels } from 'apiClient/adage'
import { defaultCollectiveTemplateOffer } from 'utils/adageFactories'

import {
  AdageOfferPublicSection,
  AdageOfferPublicSectionProps,
} from '../AdageOfferPublicSection'

function renderAdageOfferPublicSection(
  props: AdageOfferPublicSectionProps = {
    offer: defaultCollectiveTemplateOffer,
  }
) {
  return render(<AdageOfferPublicSection {...props} />)
}

describe('AdageOfferPublicSection', () => {
  it('should display the offer students levels', () => {
    renderAdageOfferPublicSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        students: [StudentLevels.COLL_GE_3E, StudentLevels.COLL_GE_6E],
      },
    })

    expect(
      screen.getByRole('heading', { name: 'Niveau scolaire' })
    ).toBeInTheDocument()
    expect(screen.getByText('Collège - 3e')).toBeInTheDocument()
    expect(screen.getByText('Collège - 6e')).toBeInTheDocument()
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
    ).toBeInTheDocument()
    expect(screen.getByText('Psychique ou cognitif')).toBeInTheDocument()
    expect(screen.getByText('Auditif')).toBeInTheDocument()
    expect(screen.getByText('Moteur')).toBeInTheDocument()
    expect(screen.getByText('Visuel')).toBeInTheDocument()
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

    expect(screen.getByText('Non accessible')).toBeInTheDocument()
  })
})

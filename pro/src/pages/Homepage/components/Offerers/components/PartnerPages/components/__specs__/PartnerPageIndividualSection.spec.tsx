import { screen } from '@testing-library/react'

import { renderWithProviders } from 'commons/utils/renderWithProviders'

import {
  PartnerPageIndividualSection,
  PartnerPageIndividualSectionProps,
} from '../PartnerPageIndividualSection'

const renderPartnerPageIndividualSection = (
  props: PartnerPageIndividualSectionProps
) => {
  renderWithProviders(<PartnerPageIndividualSection {...props} />)
}

describe('PartnerPageIndividualSection', () => {
  it('should display right info when visible and title', () => {
    const props = {
      venueId: 7,
      offererId: 8,
      venueName: 'Venue name',
    }

    renderPartnerPageIndividualSection(props)

    expect(screen.getByText('Grand public')).toBeInTheDocument()
    expect(screen.getByText('Copier le lien de la page')).toBeInTheDocument()
  })

  it('should display right info when is visible and in homepage', () => {
    const props: PartnerPageIndividualSectionProps = {
      venueId: 7,
      offererId: 8,
      venueName: 'Venue name',
    }

    renderPartnerPageIndividualSection(props)

    expect(screen.getByText('Grand public')).toBeInTheDocument()
    expect(
      screen.getByText('Gérer votre page pour le grand public')
    ).toBeInTheDocument()
    expect(screen.getByText('Copier le lien de la page')).toBeInTheDocument()
  })
})

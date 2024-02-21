import { screen } from '@testing-library/react'

import { renderWithProviders } from 'utils/renderWithProviders'

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
      isVisibleInApp: true,
      displayTitle: true,
    }

    renderPartnerPageIndividualSection(props)

    expect(screen.getByText('Grand public')).toBeInTheDocument()
    expect(screen.getByText('Visible')).toBeInTheDocument()
    expect(
      screen.getByText(
        'Votre page partenaire est visible sur l’application pass Culture.'
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Copier le lien de la page')).toBeInTheDocument()
  })

  it('should display right info when not title', () => {
    const props = {
      venueId: 7,
      isVisibleInApp: true,
      displayTitle: false,
    }

    renderPartnerPageIndividualSection(props)

    expect(screen.queryByText('Grand public')).not.toBeInTheDocument()
    expect(
      screen.getByText('État de votre page partenaire sur l’application :')
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Votre page partenaire est visible sur l’application pass Culture.'
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Copier le lien de la page')).toBeInTheDocument()
  })

  it('should display right info when not visible and not title', () => {
    const props = {
      venueId: 7,
      isVisibleInApp: false,
      displayTitle: false,
    }

    renderPartnerPageIndividualSection(props)

    expect(
      screen.getByText('État de votre page partenaire sur l’application :')
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Votre page n’est pas visible par les utilisateurs de l’application pass Culture. Vos offres publiées restent cependant visibles et réservables par les bénéficiaires.'
      )
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Copier le lien de la page')
    ).not.toBeInTheDocument()
  })
})

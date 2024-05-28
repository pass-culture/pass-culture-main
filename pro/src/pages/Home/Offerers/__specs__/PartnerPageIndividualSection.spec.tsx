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
      offererId: 8,
      venueName: 'Venue name',
      isVisibleInApp: true,
      isDisplayedInHomepage: true,
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

  it('should display right info when is visible and in homepage', () => {
    const props: PartnerPageIndividualSectionProps = {
      venueId: 7,
      offererId: 8,
      venueName: 'Venue name',
      isVisibleInApp: true,
      isDisplayedInHomepage: true,
    }

    renderPartnerPageIndividualSection(props)

    expect(screen.getByText('Grand public')).toBeInTheDocument()
    expect(
      screen.getByText('Gérer votre page pour le grand public')
    ).toBeInTheDocument()
    expect(
      screen.queryByText('État de votre page partenaire sur l’application :')
    ).not.toBeInTheDocument()
    expect(
      screen.getByText(
        'Votre page partenaire est visible sur l’application pass Culture.'
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Copier le lien de la page')).toBeInTheDocument()
  })

  it('should display right info when is visible and in venue form', () => {
    const props = {
      venueId: 7,
      offererId: 8,
      venueName: 'Venue name',
      isVisibleInApp: true,
      isDisplayedInHomepage: false,
    }

    renderPartnerPageIndividualSection(props)

    expect(screen.queryByText('Grand public')).not.toBeInTheDocument()
    expect(
      screen.getByText('État de votre page partenaire sur l’application :')
    ).toBeInTheDocument()
    expect(
      screen.queryByText(
        'Votre page partenaire est visible sur l’application pass Culture.'
      )
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('Gérer votre page pour le grand public')
    ).not.toBeInTheDocument()
    expect(screen.getByText('Copier le lien de la page')).toBeInTheDocument()
  })

  it('should display right info when not visible and not title and in venue form', () => {
    const props = {
      venueId: 7,
      offererId: 8,
      venueName: 'Venue name',
      isVisibleInApp: false,
      isDisplayedInHomepage: false,
    }

    renderPartnerPageIndividualSection(props)

    expect(
      screen.getByText('État de votre page partenaire sur l’application :')
    ).toBeInTheDocument()
    expect(
      screen.queryByText(
        'Votre page n’est pas visible par les utilisateurs de l’application pass Culture. Vos offres publiées restent cependant visibles et réservables par les bénéficiaires.'
      )
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('Copier le lien de la page')
    ).not.toBeInTheDocument()
  })
})

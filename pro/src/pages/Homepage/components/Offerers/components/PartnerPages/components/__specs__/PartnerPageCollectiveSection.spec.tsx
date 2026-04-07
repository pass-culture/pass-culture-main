import { screen } from '@testing-library/react'

import { DMSApplicationstatus } from '@/apiClient/v1'
import { defaultDMSApplicationForEAC } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  PartnerPageCollectiveSection,
  type PartnerPageCollectiveSectionProps,
} from '../PartnerPageCollectiveSection'

const renderPartnerPageCollectiveSection = (
  props: Partial<PartnerPageCollectiveSectionProps>
) => {
  renderWithProviders(
    <PartnerPageCollectiveSection
      lastCollectiveDmsApplication={defaultDMSApplicationForEAC}
      venueId={7}
      offererId={8}
      venueName="Venue name"
      allowedOnAdage={false}
      {...props}
    />
  )
}

describe('PartnerPages', () => {
  it('should display the EAC section when no adage', () => {
    renderPartnerPageCollectiveSection({
      lastCollectiveDmsApplication: null,
      allowedOnAdage: false,
    })

    expect(screen.getByText('Non référencé dans ADAGE')).toBeInTheDocument()
    expect(screen.getByText('Déposer un dossier ADAGE')).toBeInTheDocument()
  })

  it('should display the EAC section when no adage but allowed on ADAGE', () => {
    renderPartnerPageCollectiveSection({
      lastCollectiveDmsApplication: null,
      allowedOnAdage: true,
    })

    expect(screen.getByText('Référencé dans ADAGE')).toBeInTheDocument()
  })

  it('should display the EAC section when adage refused', () => {
    renderPartnerPageCollectiveSection({
      lastCollectiveDmsApplication: {
        ...defaultDMSApplicationForEAC,
        state: DMSApplicationstatus.REFUSE,
      },
    })

    expect(screen.getByText('Non référencé dans ADAGE')).toBeInTheDocument()
    expect(
      screen.queryByText('Faire une demande de référencement ADAGE')
    ).not.toBeInTheDocument()
  })

  it('should display the EAC section when adage is without following', () => {
    renderPartnerPageCollectiveSection({
      lastCollectiveDmsApplication: {
        ...defaultDMSApplicationForEAC,
        state: DMSApplicationstatus.SANS_SUITE,
      },
    })

    expect(screen.getByText('Non référencé dans ADAGE')).toBeInTheDocument()
    expect(
      screen.queryByText('Faire une demande de référencement ADAGE')
    ).not.toBeInTheDocument()
  })

  it('should display the EAC section when adage application in progress', () => {
    renderPartnerPageCollectiveSection({
      lastCollectiveDmsApplication: {
        ...defaultDMSApplicationForEAC,
        state: DMSApplicationstatus.EN_INSTRUCTION,
      },
    })

    expect(screen.getByText('Référencement en cours')).toBeInTheDocument()
  })

  it('should display the EAC section when adage application accepted but has not yet adageId', () => {
    renderPartnerPageCollectiveSection({
      lastCollectiveDmsApplication: {
        ...defaultDMSApplicationForEAC,
        state: DMSApplicationstatus.ACCEPTE,
      },
    })

    expect(screen.getByText('Référencement en cours')).toBeInTheDocument()
  })

  it('should display the EAC section when it has an adageId in homepage', () => {
    renderPartnerPageCollectiveSection({
      lastCollectiveDmsApplication: null,
      allowedOnAdage: true,
      isDisplayedInHomepage: true,
    })

    expect(screen.getByText('Référencé dans ADAGE')).toBeInTheDocument()
    expect(
      screen.getByText(/Les enseignants voient les offres vitrines/)
    ).toBeInTheDocument()
  })

  it('should display the EAC section when it has an adageId in venue form', () => {
    renderPartnerPageCollectiveSection({
      lastCollectiveDmsApplication: null,
      allowedOnAdage: true,
      isDisplayedInHomepage: false,
    })

    expect(screen.getByText('Référencé dans ADAGE')).toBeInTheDocument()
    expect(
      screen.queryByText(/es enseignants voient les offres vitrines/)
    ).not.toBeInTheDocument()
  })
})

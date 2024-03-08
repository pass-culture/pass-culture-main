import { screen } from '@testing-library/react'
import * as router from 'react-router-dom'

import { DMSApplicationstatus, VenueTypeCode } from 'apiClient/v1'
import { defaultDMSApplicationForEAC } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  PartnerPageCollectiveSection,
  PartnerPageCollectiveSectionProps,
} from '../PartnerPageCollectiveSection'

const renderPartnerPageCollectiveSection = (
  props: Partial<PartnerPageCollectiveSectionProps>
) => {
  renderWithProviders(
    <PartnerPageCollectiveSection
      collectiveDmsApplications={[defaultDMSApplicationForEAC]}
      venueId={7}
      allowedOnAdage={false}
      {...props}
    />
  )
}

vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) ?? {}),
  useLoaderData: vi.fn(),
}))

describe('PartnerPages', () => {
  beforeEach(() => {
    vi.spyOn(router, 'useLoaderData').mockReturnValue({
      venueTypes: [{ id: VenueTypeCode.FESTIVAL, label: 'Festival' }],
    })
  })

  it('should display the EAC section when no adage', () => {
    renderPartnerPageCollectiveSection({
      collectiveDmsApplications: [],
      allowedOnAdage: false,
    })

    expect(screen.getByText('Non référencé dans ADAGE')).toBeInTheDocument()
    expect(
      screen.getByText('Faire une demande de référencement ADAGE')
    ).toBeInTheDocument()
  })

  it('should display the EAC section when no adage but allowed on Adage', () => {
    renderPartnerPageCollectiveSection({
      collectiveDmsApplications: [],
      allowedOnAdage: true,
    })

    expect(screen.getByText('Référencé dans ADAGE')).toBeInTheDocument()
  })

  it('should display the EAC section when adage refused', () => {
    renderPartnerPageCollectiveSection({
      collectiveDmsApplications: [
        {
          ...defaultDMSApplicationForEAC,
          state: DMSApplicationstatus.REFUSE,
        },
      ],
    })

    expect(screen.getByText('Non référencé dans ADAGE')).toBeInTheDocument()
    expect(
      screen.queryByText('Faire une demande de référencement ADAGE')
    ).not.toBeInTheDocument()
  })

  it('should display the EAC section when adage is without following', () => {
    renderPartnerPageCollectiveSection({
      collectiveDmsApplications: [
        {
          ...defaultDMSApplicationForEAC,
          state: DMSApplicationstatus.SANS_SUITE,
        },
      ],
    })

    expect(screen.getByText('Non référencé dans ADAGE')).toBeInTheDocument()
    expect(
      screen.queryByText('Faire une demande de référencement ADAGE')
    ).not.toBeInTheDocument()
  })

  it('should display the EAC section when adage application in progress', () => {
    renderPartnerPageCollectiveSection({
      collectiveDmsApplications: [
        {
          ...defaultDMSApplicationForEAC,
          state: DMSApplicationstatus.EN_INSTRUCTION,
        },
      ],
    })

    expect(screen.getByText('Référencement en cours')).toBeInTheDocument()
  })

  it('should display the EAC section when adage application accepted but has not yet adageId', () => {
    renderPartnerPageCollectiveSection({
      collectiveDmsApplications: [
        {
          ...defaultDMSApplicationForEAC,
          state: DMSApplicationstatus.ACCEPTE,
        },
      ],
    })

    expect(screen.getByText('Référencement en cours')).toBeInTheDocument()
  })

  it('should display the EAC section when it has an adageId in homepage', () => {
    renderPartnerPageCollectiveSection({
      collectiveDmsApplications: [],
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
      collectiveDmsApplications: [],
      allowedOnAdage: true,
      isDisplayedInHomepage: false,
    })

    expect(screen.getByText('Référencé dans ADAGE')).toBeInTheDocument()
    expect(
      screen.queryByText(/es enseignants voient les offres vitrines/)
    ).not.toBeInTheDocument()
  })
})

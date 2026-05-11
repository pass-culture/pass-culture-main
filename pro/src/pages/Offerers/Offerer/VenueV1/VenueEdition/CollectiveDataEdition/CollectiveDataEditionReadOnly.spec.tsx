import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import {
  DisplayableActivity,
  type GetVenueResponseModel,
  StudentLevels,
} from '@/apiClient/v1'
import { getActivityLabel } from '@/commons/mappings/mappings'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveDataEditionReadOnly } from './CollectiveDataEditionReadOnly'

const renderCollectiveDataEditionReadOnly = (
  venueOverrides: Partial<GetVenueResponseModel> = {}
) =>
  renderWithProviders(<CollectiveDataEditionReadOnly />, {
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: 1,
          ...venueOverrides,
        }),
      },
    },
  })

describe('<CollectiveDataEditionReadOnly />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderCollectiveDataEditionReadOnly()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display collective description', () => {
    renderCollectiveDataEditionReadOnly({
      collectiveDescription: 'Notre démarche éducative',
    })

    expect(screen.getByText('Notre démarche éducative')).toBeInTheDocument()
  })

  it('should display "Non renseignée" when collective description is not provided', () => {
    renderCollectiveDataEditionReadOnly({
      collectiveDescription: null,
    })

    expect(screen.getAllByText('Non renseignée').length).toBeGreaterThanOrEqual(
      1
    )
  })

  it('should display collective students', () => {
    renderCollectiveDataEditionReadOnly({
      collectiveStudents: [StudentLevels.COLL_GE_4E, StudentLevels.COLL_GE_3E],
    })

    expect(screen.getByText('Collège - 4e, Collège - 3e')).toBeInTheDocument()
  })

  it('should display collective website', () => {
    renderCollectiveDataEditionReadOnly({
      collectiveWebsite: 'https://example.com',
    })

    expect(screen.getByText('https://example.com')).toBeInTheDocument()
  })

  it('should display activity when provided', () => {
    renderCollectiveDataEditionReadOnly({
      activity: DisplayableActivity.PERFORMANCE_HALL,
    })

    expect(screen.getByText(/Activité/i)).toBeInTheDocument()
    expect(
      screen.getByText(getActivityLabel(DisplayableActivity.PERFORMANCE_HALL))
    ).toBeInTheDocument()
  })

  it('should display collective domains', () => {
    renderCollectiveDataEditionReadOnly({
      collectiveDomains: [
        { id: 1, name: 'Arts visuels' },
        { id: 2, name: 'Danse' },
      ],
    })

    expect(screen.getByText('Arts visuels, Danse')).toBeInTheDocument()
  })

  it('should display "Non renseigné" when collective domains are empty', () => {
    renderCollectiveDataEditionReadOnly({
      collectiveDomains: [],
    })

    expect(
      screen.getByText(/Domaine artistique et culturel/i)
    ).toBeInTheDocument()
    expect(screen.getAllByText('Non renseigné').length).toBeGreaterThanOrEqual(
      1
    )
  })

  it('should display collective domains in plural if there are multiple domains', () => {
    renderCollectiveDataEditionReadOnly({
      collectiveDomains: [
        { id: 1, name: 'Arts visuels' },
        { id: 2, name: 'Danse' },
      ],
    })

    expect(
      screen.getByText(/Domaines artistiques et culturels/)
    ).toBeInTheDocument()
  })

  it('should display collective intervention area', () => {
    renderCollectiveDataEditionReadOnly({
      collectiveInterventionArea: ['75'],
    })

    expect(screen.getByText(/Zone de mobilité/i)).toBeInTheDocument()
  })

  it('should display collective intervention area in plural if there are multiple areas', () => {
    renderCollectiveDataEditionReadOnly({
      collectiveInterventionArea: ['75', '92'],
    })

    expect(screen.getByText(/Zones de mobilité/)).toBeInTheDocument()
  })

  it('should display collective legal status', () => {
    renderCollectiveDataEditionReadOnly({
      collectiveLegalStatus: { id: 1, name: 'Association' },
    })

    expect(screen.getByText('Association')).toBeInTheDocument()
  })

  it('should display collective phone', () => {
    renderCollectiveDataEditionReadOnly({
      collectivePhone: '0123456789',
    })

    expect(screen.getByText('0123456789')).toBeInTheDocument()
  })

  it('should display collective email', () => {
    renderCollectiveDataEditionReadOnly({
      collectiveEmail: 'contact@example.com',
    })

    expect(screen.getByText('contact@example.com')).toBeInTheDocument()
  })

  it('should display edit link with correct path', () => {
    renderCollectiveDataEditionReadOnly({
      id: 42,
      managingOfferer: {
        id: 10,
        name: 'Test Offerer',
        isValidated: true,
        siren: '123456789',
      },
    })

    const editLink = screen.getByRole('link', {
      name: /Modifier/,
    })
    expect(editLink).toHaveAttribute(
      'href',
      '/partenaire/page-collective/edition'
    )
  })
})

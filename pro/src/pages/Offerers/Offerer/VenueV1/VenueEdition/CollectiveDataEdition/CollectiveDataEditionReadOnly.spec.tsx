import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { DisplayableActivity, StudentLevels } from '@/apiClient/v1'
import { getActivityLabel } from '@/commons/mappings/mappings'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveDataEditionReadOnly } from './CollectiveDataEditionReadOnly'

describe('<CollectiveDataEditionReadOnly />', () => {
  it('should render without accessibility violations', async () => {
    const venue = makeGetVenueResponseModel({ id: 1 })
    const { container } = renderWithProviders(
      <CollectiveDataEditionReadOnly venue={venue} />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display collective description', () => {
    const venue = makeGetVenueResponseModel({
      id: 1,
      collectiveDescription: 'Notre démarche éducative',
    })

    renderWithProviders(<CollectiveDataEditionReadOnly venue={venue} />)

    expect(screen.getByText('Notre démarche éducative')).toBeInTheDocument()
  })

  it('should display "Non renseignée" when collective description is not provided', () => {
    const venue = makeGetVenueResponseModel({
      id: 1,
      collectiveDescription: null,
    })

    renderWithProviders(<CollectiveDataEditionReadOnly venue={venue} />)

    expect(screen.getAllByText('Non renseignée').length).toBeGreaterThanOrEqual(
      1
    )
  })

  it('should display collective students', () => {
    const venue = makeGetVenueResponseModel({
      id: 1,
      collectiveStudents: [StudentLevels.COLL_GE_4E, StudentLevels.COLL_GE_3E],
    })

    renderWithProviders(<CollectiveDataEditionReadOnly venue={venue} />)

    expect(screen.getByText('Collège - 4e, Collège - 3e')).toBeInTheDocument()
  })

  it('should display collective website', () => {
    const venue = makeGetVenueResponseModel({
      id: 1,
      collectiveWebsite: 'https://example.com',
    })

    renderWithProviders(<CollectiveDataEditionReadOnly venue={venue} />)

    expect(screen.getByText('https://example.com')).toBeInTheDocument()
  })

  it('should display activity when provided', () => {
    const venue = makeGetVenueResponseModel({
      id: 1,
      activity: DisplayableActivity.PERFORMANCE_HALL,
    })

    renderWithProviders(<CollectiveDataEditionReadOnly venue={venue} />)

    expect(screen.getByText(/Activité/i)).toBeInTheDocument()
    expect(
      screen.getByText(getActivityLabel(DisplayableActivity.PERFORMANCE_HALL))
    ).toBeInTheDocument()
  })

  it('should display collective domains', () => {
    const venue = makeGetVenueResponseModel({
      id: 1,
      collectiveDomains: [
        { id: 1, name: 'Arts visuels' },
        { id: 2, name: 'Danse' },
      ],
    })

    renderWithProviders(<CollectiveDataEditionReadOnly venue={venue} />)

    expect(screen.getByText('Arts visuels, Danse')).toBeInTheDocument()
  })

  it('should display "Non renseigné" when collective domains are empty', () => {
    const venue = makeGetVenueResponseModel({
      id: 1,
      collectiveDomains: [],
    })

    renderWithProviders(<CollectiveDataEditionReadOnly venue={venue} />)

    expect(
      screen.getByText(/Domaine artistique et culturel/i)
    ).toBeInTheDocument()
    expect(screen.getAllByText('Non renseigné').length).toBeGreaterThanOrEqual(
      1
    )
  })

  it('should display collective domains in plural if there are multiple domains', () => {
    const venue = makeGetVenueResponseModel({
      id: 1,
      collectiveDomains: [
        { id: 1, name: 'Arts visuels' },
        { id: 2, name: 'Danse' },
      ],
    })

    renderWithProviders(<CollectiveDataEditionReadOnly venue={venue} />)

    expect(
      screen.getByText(/Domaines artistiques et culturels/)
    ).toBeInTheDocument()
  })

  it('should display collective intervention area', () => {
    const venue = makeGetVenueResponseModel({
      id: 1,
      collectiveInterventionArea: ['75'],
    })

    renderWithProviders(<CollectiveDataEditionReadOnly venue={venue} />)

    expect(screen.getByText(/Zone de mobilité/i)).toBeInTheDocument()
  })

  it('should display collective intervention area in plural if there are multiple areas', () => {
    const venue = makeGetVenueResponseModel({
      id: 1,
      collectiveInterventionArea: ['75', '92'],
    })

    renderWithProviders(<CollectiveDataEditionReadOnly venue={venue} />)

    expect(screen.getByText(/Zones de mobilité/)).toBeInTheDocument()
  })

  it('should display collective legal status', () => {
    const venue = makeGetVenueResponseModel({
      id: 1,
      collectiveLegalStatus: { id: 1, name: 'Association' },
    })

    renderWithProviders(<CollectiveDataEditionReadOnly venue={venue} />)

    expect(screen.getByText('Association')).toBeInTheDocument()
  })

  it('should display collective phone', () => {
    const venue = makeGetVenueResponseModel({
      id: 1,
      collectivePhone: '0123456789',
    })

    renderWithProviders(<CollectiveDataEditionReadOnly venue={venue} />)

    expect(screen.getByText('0123456789')).toBeInTheDocument()
  })

  it('should display collective email', () => {
    const venue = makeGetVenueResponseModel({
      id: 1,
      collectiveEmail: 'contact@example.com',
    })

    renderWithProviders(<CollectiveDataEditionReadOnly venue={venue} />)

    expect(screen.getByText('contact@example.com')).toBeInTheDocument()
  })

  it('should display edit link with correct path', () => {
    const venue = makeGetVenueResponseModel({
      id: 42,
      managingOfferer: {
        id: 10,
        name: 'Test Offerer',
        isValidated: true,
        siren: '123456789',
      },
    })

    renderWithProviders(<CollectiveDataEditionReadOnly venue={venue} />)

    const editLink = screen.getByRole('link', {
      name: /Modifier/,
    })
    expect(editLink).toHaveAttribute(
      'href',
      '/structures/10/lieux/42/collectif/edition'
    )
  })
})

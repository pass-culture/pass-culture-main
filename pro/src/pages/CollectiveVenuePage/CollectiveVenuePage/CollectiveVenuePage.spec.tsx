import { screen } from '@testing-library/react'

import {
  DisplayableActivity,
  type GetVenueResponseModel,
  StudentLevels,
} from '@/apiClient/v1/new'
import { DisplayableActivityMap } from '@/commons/mappings/DisplayableActivity'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveVenuePage } from './CollectiveVenuePage'

const renderCollectiveVenuePage = (
  venueOverrides: Partial<GetVenueResponseModel> = {}
) =>
  renderWithProviders(<CollectiveVenuePage />, {
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: 7,
          ...venueOverrides,
        }),
      },
    },
  })

describe('CollectiveVenuePage', () => {
  it('should display the section and sub-section titles', () => {
    renderCollectiveVenuePage()

    expect(
      screen.getByText('Vos informations pour les enseignants')
    ).toBeVisible()
    expect(screen.getByText('Présentation pour les enseignants')).toBeVisible()
    expect(screen.getByText('Informations de la structure')).toBeVisible()
    expect(screen.getByText('Contact')).toBeVisible()
  })

  it('should display fallback labels when the collective data is empty', () => {
    renderCollectiveVenuePage()

    expect(screen.getAllByText('Non renseignée').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Non renseigné').length).toBeGreaterThan(0)
  })

  it('should not display the activity row when the venue has no activity', () => {
    renderCollectiveVenuePage({ activity: null })

    expect(screen.queryByText(/Activité/)).not.toBeInTheDocument()
  })

  it('should display the populated collective data', () => {
    renderCollectiveVenuePage({
      activity: DisplayableActivity.FESTIVAL,
      collectiveDescription: 'Notre démarche EAC',
      collectiveStudents: [StudentLevels.COLL_GE_6E, StudentLevels.COLL_GE_5E],
      collectiveWebsite: 'https://example.com',
      collectiveDomains: [
        { id: 1, name: 'Danse' },
        { id: 2, name: 'Musique' },
      ],
      collectiveInterventionArea: ['01'],
      collectiveLegalStatus: { id: 1, name: 'Association' },
      collectivePhone: '+33612345678',
      collectiveEmail: 'contact@example.com',
    })

    expect(screen.getByText(/Activité/)).toBeVisible()
    expect(
      screen.getByText(DisplayableActivityMap.get('FESTIVAL') ?? '')
    ).toBeVisible()
    expect(screen.getByText('Notre démarche EAC')).toBeVisible()
    expect(screen.getByText('Collège - 6e, Collège - 5e')).toBeVisible()
    expect(screen.getByText('https://example.com')).toBeVisible()
    expect(screen.getByText('Danse, Musique')).toBeVisible()
    expect(screen.getByText('Ain (01)')).toBeVisible()
    expect(screen.getByText('Association')).toBeVisible()
    expect(screen.getByText('+33 6 12 34 56 78')).toBeVisible()
    expect(screen.getByText('contact@example.com')).toBeVisible()
  })
})

import { screen } from '@testing-library/react'
import type { SWRResponse } from 'swr'

import {
  DisplayableActivity,
  type EducationalDomainsResponseModel,
  type GetVenueResponseModel,
} from '@/apiClient/v1/new'
import * as useEducationalDomainsModule from '@/commons/hooks/swr/useEducationalDomains'
import { getActivityLabel } from '@/commons/mappings/mappings'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ActivitySubSection } from './ActivitySubSection'

const mockEducationalDomains = (data: EducationalDomainsResponseModel) => {
  vi.spyOn(
    useEducationalDomainsModule,
    'useEducationalDomains'
  ).mockReturnValue({ isLoading: false, data } as SWRResponse)
}

const renderActivitySubSection = (
  venueOverrides: Partial<GetVenueResponseModel> = {}
) =>
  renderWithProviders(<ActivitySubSection />, {
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

describe('ActivitySubSection', () => {
  it('should display the activity, the domains and the description', () => {
    mockEducationalDomains([{ id: 1, name: 'Danse', nationalPrograms: [] }])

    renderActivitySubSection({
      activity: DisplayableActivity.OTHER,
      collectiveDomains: [{ id: 1, name: 'Danse' }],
      description: 'Ma description',
    })

    expect(
      screen.getByText(getActivityLabel(DisplayableActivity.OTHER))
    ).toBeInTheDocument()
    expect(screen.getByText('Danse')).toBeInTheDocument()
    expect(screen.getByText('Ma description')).toBeInTheDocument()
  })

  it('should omit the activity and domains rows and fall back to a placeholder description', () => {
    mockEducationalDomains([])

    renderActivitySubSection({
      activity: null,
      collectiveDomains: [],
      description: null,
    })

    expect(
      screen.queryByText(getActivityLabel(DisplayableActivity.OTHER))
    ).not.toBeInTheDocument()
    expect(screen.getByText(/Description/)).toBeInTheDocument()
    expect(screen.getByText('Non renseignée')).toBeInTheDocument()
  })
})

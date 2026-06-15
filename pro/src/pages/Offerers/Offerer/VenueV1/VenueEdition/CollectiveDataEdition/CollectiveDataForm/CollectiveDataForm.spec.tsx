import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect, vi } from 'vitest'

import { apiNew } from '@/apiClient/api'
import {
  DisplayableActivity,
  type GetVenueResponseModel,
} from '@/apiClient/v1/new'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { CollectiveDataForm } from '../CollectiveDataForm/CollectiveDataForm'

const mockMutate = vi.fn()

vi.mock('@/apiClient/api', () => ({
  apiNew: {
    editVenueCollectiveData: vi.fn(),
  },
}))

vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router')
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  }
})

vi.mock('swr', async () => {
  const actual = await vi.importActual('swr')
  return {
    ...actual,
    useSWRConfig: () => ({ mutate: mockMutate }),
  }
})

function renderCollectiveDataForm(
  options?: RenderWithProvidersOptions,
  venueOverrides?: Partial<GetVenueResponseModel>
) {
  return renderWithProviders(
    <CollectiveDataForm
      statuses={[
        {
          value: '1',
          label: 'statut 1',
        },
        {
          value: '2',
          label: 'statut 2',
        },
      ]}
    />,
    {
      ...options,
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
          selectedPartnerVenue: makeGetVenueResponseModel({
            ...defaultGetVenue,
            ...venueOverrides,
          }),
        },
        ...options?.storeOverrides,
      },
    }
  )
}

describe('CollectiveDataForm', () => {
  it('should check collective student', async () => {
    renderCollectiveDataForm()

    await userEvent.click(screen.getByLabelText('Public cible'))

    const studentCheckbox = screen.getByRole('checkbox', {
      name: 'Collège - 5e',
    })

    await userEvent.click(studentCheckbox)

    expect(studentCheckbox).toBeChecked()
  })

  it('should show all student levels when ENABLE_MARSEILLE is on', async () => {
    const featureOverrides = {
      features: ['ENABLE_MARSEILLE'],
    }

    renderCollectiveDataForm(featureOverrides)

    await userEvent.click(screen.getByLabelText('Public cible'))

    expect(
      screen.getByRole('checkbox', { name: 'Écoles Marseille - Maternelle' })
    ).toBeInTheDocument()
  })

  it('should show student levels without Marseille options when ENABLE_MARSEILLE is off', async () => {
    renderCollectiveDataForm()

    await userEvent.click(screen.getByLabelText('Public cible'))

    expect(
      screen.queryByText('Écoles Marseille - Maternelle')
    ).not.toBeInTheDocument()
  })

  it('should display the collective domains as a read-only list', () => {
    renderCollectiveDataForm(
      {},
      {
        collectiveDomains: [
          { id: 1, name: 'Architecture' },
          { id: 2, name: 'Arts numériques' },
        ],
      }
    )

    expect(
      screen.getByText('Architecture, Arts numériques')
    ).toBeInTheDocument()
  })

  it('should display "Non renseigné" when there is no collective domain', () => {
    renderCollectiveDataForm({}, { collectiveDomains: [] })

    expect(screen.getByText('Non renseigné')).toBeInTheDocument()
  })

  it('should display the activity as a read-only label', () => {
    renderCollectiveDataForm({}, { activity: DisplayableActivity.CINEMA })

    expect(screen.getByText('Cinéma')).toBeInTheDocument()
  })

  it('should display "Non renseignée" when activity is null', () => {
    renderCollectiveDataForm({}, { activity: null })

    expect(screen.getByText('Non renseignée')).toBeInTheDocument()
  })

  it('should dispatch setSelectedPartnerVenue', async () => {
    mockMutate.mockClear()
    const updatedVenue = {
      ...defaultGetVenue,
      collectiveDescription: 'Updated',
    }
    vi.mocked(apiNew.editVenueCollectiveData).mockResolvedValue(updatedVenue)

    const { store } = renderCollectiveDataForm()

    const submitButton = screen.getByRole('button', { name: 'Enregistrer' })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(apiNew.editVenueCollectiveData).toHaveBeenCalledWith({
        path: { venue_id: defaultGetVenue.id },
        body: expect.any(Object),
      })
    })

    await waitFor(() => {
      expect(
        store.getState().user?.selectedPartnerVenue?.collectiveDescription
      ).toBe('Updated')
    })

    expect(mockMutate).not.toHaveBeenCalled()
  })
})

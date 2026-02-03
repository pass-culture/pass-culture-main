import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect, vi } from 'vitest'

import { api } from '@/apiClient/api'
import {
  ActivityOpenToPublic,
  type GetVenueResponseModel,
} from '@/apiClient/v1'
import { GET_VENUE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { CollectiveDataForm } from '../CollectiveDataForm/CollectiveDataForm'

const mockMutate = vi.fn()

vi.mock('@/apiClient/api', () => ({
  api: {
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
  venueOverrides?: GetVenueResponseModel
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
      domains={[
        { id: '1', label: 'Arts numériques' },
        { id: '2', label: 'Architecture' },
      ]}
      venue={{ ...defaultGetVenue, ...venueOverrides }}
    />,
    options
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

  it('should check collective domains', async () => {
    renderCollectiveDataForm()

    await userEvent.click(screen.getByLabelText('Domaines artistiques'))

    const domainsCheckbox = screen.getByRole('checkbox', {
      name: 'Architecture',
    })

    await userEvent.click(domainsCheckbox)

    expect(domainsCheckbox).toBeChecked()
  })

  it('should check activity field', async () => {
    renderCollectiveDataForm()

    const activityField = screen.getByRole('combobox', {
      name: /Activité principale/,
    })

    await userEvent.selectOptions(
      activityField,
      screen.getByRole('option', { name: 'Cinéma' })
    )

    expect(activityField).toHaveValue(ActivityOpenToPublic.CINEMA)
  })

  it('should have blank activity field is activity is null', () => {
    renderCollectiveDataForm({}, { ...defaultGetVenue, activity: null })

    const activityField = screen.getByRole('combobox', {
      name: /Activité principale/,
    })

    expect(activityField).toHaveValue('')
  })

  it('should dispatch setSelectedVenue when WIP_SWITCH_VENUE is enabled', async () => {
    mockMutate.mockClear()
    const updatedVenue = {
      ...defaultGetVenue,
      collectiveDescription: 'Updated',
    }
    vi.mocked(api.editVenueCollectiveData).mockResolvedValue(updatedVenue)

    const { store } = renderCollectiveDataForm({
      features: ['WIP_SWITCH_VENUE'],
    })

    const submitButton = screen.getByRole('button', { name: 'Enregistrer' })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(api.editVenueCollectiveData).toHaveBeenCalledWith(
        defaultGetVenue.id,
        expect.any(Object)
      )
    })

    await waitFor(() => {
      expect(store.getState().user?.selectedVenue?.collectiveDescription).toBe(
        'Updated'
      )
    })

    expect(mockMutate).not.toHaveBeenCalled()
  })

  it('should call mutate when WIP_SWITCH_VENUE is disabled', async () => {
    mockMutate.mockClear()
    const updatedVenue = {
      ...defaultGetVenue,
      collectiveDescription: 'Updated',
    }
    vi.mocked(api.editVenueCollectiveData).mockResolvedValue(updatedVenue)

    renderCollectiveDataForm()

    const submitButton = screen.getByRole('button', { name: 'Enregistrer' })
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(api.editVenueCollectiveData).toHaveBeenCalledWith(
        defaultGetVenue.id,
        expect.any(Object)
      )
    })

    expect(mockMutate).toHaveBeenCalledWith([
      GET_VENUE_QUERY_KEY,
      String(defaultGetVenue.id),
    ])
  })
})

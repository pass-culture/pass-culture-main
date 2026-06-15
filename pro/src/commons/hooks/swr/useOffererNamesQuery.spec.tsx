import { screen, waitFor } from '@testing-library/react'

import { apiNew } from '@/apiClient/api'
import type { DeepPartial } from '@/commons/custom_types/utils'
import type { RootState } from '@/commons/store/store'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { useOffererNamesQuery } from './useOffererNamesQuery'

vi.mock('@/apiClient/api', () => ({
  apiNew: {
    listOfferersNames: vi.fn(),
  },
}))

const user = sharedCurrentUserFactory()

const TestComponent = () => {
  const offererNamesQuery = useOffererNamesQuery()

  const offererNames = offererNamesQuery.data

  return (
    <div data-testid="offerernamesquery-hook">
      <ul>
        {offererNames?.map((offererName) => (
          <li key={offererName.id}>{offererName.name}</li>
        ))}
      </ul>
    </div>
  )
}

const renderComponent = (
  overrides: DeepPartial<RootState> = {
    user: {
      offererNames: null,
    },
  }
) => {
  return renderWithProviders(<TestComponent />, {
    user,
    storeOverrides: overrides,
  })
}

describe('useOffererNamesQuery', () => {
  it('should invoke API and dispatch if no data is present in the store', async () => {
    const expectedOfferersNames = [
      { id: 1, name: 'Offerer 1', validated: true },
      { id: 2, name: 'Offerer 2', validated: true },
      { id: 3, name: 'Offerer 3', validated: false },
    ]
    vi.mocked(apiNew.listOfferersNames).mockResolvedValueOnce({
      offerersNames: expectedOfferersNames,
    })

    const { store } = renderComponent()

    await waitFor(() => {
      expect(apiNew.listOfferersNames).toHaveBeenCalledTimes(1)
    })

    expect(store.getState().user.offererNames).toEqual(expectedOfferersNames)

    expect(screen.getByText('Offerer 1')).toBeInTheDocument()
    expect(screen.getByText('Offerer 2')).toBeInTheDocument()
    expect(screen.getByText('Offerer 3')).toBeInTheDocument()
  })

  it('should not invoke API and dispatch if data is present in the store', async () => {
    const mockOffererNames = [
      { id: 3, name: 'Offerer 3', validated: true },
      { id: 4, name: 'Offerer 4', validated: true },
      { id: 5, name: 'Offerer 5', validated: false },
    ]

    renderComponent({
      user: {
        offererNames: mockOffererNames,
      },
    })

    await waitFor(() => {
      expect(screen.getByText('Offerer 3')).toBeInTheDocument()
      expect(screen.getByText('Offerer 4')).toBeInTheDocument()
    })

    expect(apiNew.listOfferersNames).not.toHaveBeenCalled()
  })
})

import { screen, waitFor } from '@testing-library/react'

import { api } from '@/apiClient/api'
import type { DeepPartial } from '@/commons/custom_types/utils'
import type { RootState } from '@/commons/store/store'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { useOffererNamesQuery } from './useOffererNamesQuery'

vi.mock('@/apiClient/api', () => ({
  api: {
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
    offerer: {
      offererNamesValidated: null,
      offerersNamesWithPendingValidation: null,
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
    const expectedOfferersNamesValidated = [
      { id: 1, name: 'Offerer 1' },
      { id: 2, name: 'Offerer 2' },
    ]
    const expectedOfferersNamesWithPendingValidation = [
      { id: 3, name: 'Offerer 3' },
    ]
    vi.mocked(api.listOfferersNames).mockResolvedValueOnce({
      offerersNames: expectedOfferersNamesValidated,
      offerersNamesWithPendingValidation:
        expectedOfferersNamesWithPendingValidation,
    })

    const { store } = renderComponent()

    await waitFor(() => {
      expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
    })

    expect(store.getState().offerer.offererNamesValidated).toEqual(
      expectedOfferersNamesValidated
    )
    expect(store.getState().offerer.offerersNamesWithPendingValidation).toEqual(
      expectedOfferersNamesWithPendingValidation
    )

    expect(screen.getByText('Offerer 1')).toBeInTheDocument()
    expect(screen.getByText('Offerer 2')).toBeInTheDocument()
    expect(screen.getByText('Offerer 3')).toBeInTheDocument()
  })

  it('should not invoke API and dispatch if data is present in the store', async () => {
    const mockOffererNamesValidated = [
      { id: 3, name: 'Offerer 3' },
      { id: 4, name: 'Offerer 4' },
    ]
    const mockOfferersNamesWithPendingValidation = [
      { id: 5, name: 'Offerer 5' },
    ]

    renderComponent({
      offerer: {
        offererNamesValidated: mockOffererNamesValidated,
        offerersNamesWithPendingValidation:
          mockOfferersNamesWithPendingValidation,
      },
    })

    await waitFor(() => {
      expect(screen.getByText('Offerer 3')).toBeInTheDocument()
      expect(screen.getByText('Offerer 4')).toBeInTheDocument()
    })

    expect(api.listOfferersNames).not.toHaveBeenCalled()
  })
})

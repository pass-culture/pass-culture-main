import { screen, waitFor } from '@testing-library/react'

import { api } from '@/apiClient//api'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { useOffererNamesQuery } from './useOffererNamesQuery'

vi.mock('@/apiClient//api', () => ({
  api: {
    listOfferersNames: vi.fn(),
  },
}))

const mockDispatch = vi.fn()
vi.mock('react-redux', async () => {
  const actual = await vi.importActual('react-redux')
  return {
    ...actual,
    useDispatch: () => mockDispatch,
  }
})

const user = sharedCurrentUserFactory()

const TestComponent = () => {
  const offererNamesQuery = useOffererNamesQuery()

  const offererNames = offererNamesQuery.data?.offerersNames

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
  overrides: any = {
    offerer: {
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
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should invoke API and dispatch if no data is present in the store', async () => {
    const mockOffererNames = [
      { id: 1, name: 'Offerer 1', allowedOnAdage: false },
      { id: 2, name: 'Offerer 2', allowedOnAdage: true },
    ]

    vi.mocked(api.listOfferersNames).mockResolvedValueOnce({
      offerersNames: mockOffererNames,
    })

    renderComponent()

    await waitFor(() => {
      expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
      expect(mockDispatch).toHaveBeenCalledWith(
        expect.objectContaining({
          payload: mockOffererNames,
        })
      )
    })

    expect(screen.getByText('Offerer 1')).toBeInTheDocument()
    expect(screen.getByText('Offerer 2')).toBeInTheDocument()
  })

  it('should not invoke API and dispatch if data is present in the store', async () => {
    const mockOffererNames = [
      { id: 3, name: 'Offerer 3', allowedOnAdage: true },
      { id: 4, name: 'Offerer 4', allowedOnAdage: false },
    ]

    renderComponent({
      offerer: {
        offererNames: mockOffererNames,
      },
    })

    await waitFor(() => {
      expect(screen.getByText('Offerer 3')).toBeInTheDocument()
      expect(screen.getByText('Offerer 4')).toBeInTheDocument()
    })

    expect(api.listOfferersNames).not.toHaveBeenCalled()
    expect(mockDispatch).not.toHaveBeenCalled()
  })
})

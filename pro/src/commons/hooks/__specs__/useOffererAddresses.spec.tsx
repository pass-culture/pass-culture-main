import { api } from 'apiClient/api'
import { screen, waitFor } from '@testing-library/react'
import { useOffererAddresses } from 'commons/hooks/swr/useOffererAddresses'
import { offererAddressFactory } from 'commons/utils/factories/offererAddressFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { beforeEach, expect } from 'vitest'

vi.mock('apiClient/api', () => ({
  api: {
    getOffererAddresses: vi.fn(),
  },
}))
const user = sharedCurrentUserFactory()

const TestComponent = () => {
  return (
    <div data-testid="addresses-length">
      {useOffererAddresses().data.length}
    </div>
  )
}

const renderComponent = (
  overrides: any = {
    user: { currentUser: user },
    offerer: currentOffererFactory(),
  }
) => {
  return renderWithProviders(<TestComponent />, {
    user,
    storeOverrides: overrides,
  })
}

describe('useOffererAddresses', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOffererAddresses').mockResolvedValue([
      offererAddressFactory({
        label: 'Label',
      }),
      offererAddressFactory({
        city: 'New York',
      }),
    ])
  })

  it('should return a result when an offerer is set', async () => {
    renderComponent()

    await waitFor(() => {
      expect(api.getOffererAddresses).toHaveBeenCalled()
    })

    expect(screen.getByTestId('addresses-length').innerHTML).toEqual('2')
  })

  it('should return an empty list when no offerer is set', async () => {
    renderComponent({
      user: { currentUser: user },
      offerer: {
        offererNames: [],
        currentOfferer: null,
      },
    })

    await waitFor(() => {
      expect(api.getOffererAddresses).not.toHaveBeenCalled()
    })

    expect(screen.getByTestId('addresses-length').innerHTML).toEqual('0')
  })
})

import { act, renderHook } from '@testing-library/react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'

import { api } from 'apiClient/api'
import { useLogout } from 'hooks/useLogout'
import { configureTestStore } from 'store/testUtils'

describe('useLogout', () => {
  it('should return a function to logout', async () => {
    const store = configureTestStore()

    const wrapper = ({ children }: { children: any }) => (
      <Provider store={store}>
        <MemoryRouter initialEntries={['/']}>{children}</MemoryRouter>
      </Provider>
    )

    const { result } = renderHook(() => useLogout(), { wrapper })

    vi.spyOn(api, 'signout').mockResolvedValue()
    await act(() => result.current())

    expect(api.signout).toHaveBeenCalledTimes(1)
  })
})

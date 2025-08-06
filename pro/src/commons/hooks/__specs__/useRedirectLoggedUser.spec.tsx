import { renderHook } from '@testing-library/react'
import * as reactRedux from 'react-redux'
import { MemoryRouter } from 'react-router'

import { api } from '@/apiClient/api'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'

import { useRedirectLoggedUser } from '../useRedirectLoggedUser'

const mockNavigate = vi.fn()
const mockDispatch = vi.fn()

vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

vi.mock('react-redux', () => ({
  ...vi.importActual('react-redux'),
  useSelector: vi.fn(),
  useDispatch: () => mockDispatch,
}))

vi.mock('@/apiClient/api', () => ({
  api: {
    listOfferersNames: vi.fn(),
  },
}))
vi.mock('@/commons/hooks/useActiveFeature', () => ({
  useActiveFeature: vi.fn(),
}))

const renderUseRedirectLoggedUser = (url: string) => {
  const wrapper = ({ children }: { children: any }) => (
    <MemoryRouter initialEntries={[url]}>{children}</MemoryRouter>
  )

  return renderHook(() => useRedirectLoggedUser(), {
    wrapper,
  })
}

describe('useRedirectLoggedUser', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(reactRedux.useSelector).mockReturnValue({ id: 123 }) // mock logged in user
    vi.mocked(useActiveFeature).mockReturnValue(false)
  })

  it('should redirect to /inscription/structure/recherche page if user has no offerer names', async () => {
    // Mock empty offerer names array
    vi.mocked(useActiveFeature).mockReturnValueOnce(true)
    vi.mocked(api.listOfferersNames).mockResolvedValue({ offerersNames: [] })

    renderUseRedirectLoggedUser('/')

    // Wait for the effect to run
    await vi.waitFor(() => {
      expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
      expect(mockNavigate).toHaveBeenCalledWith(
        '/inscription/structure/recherche'
      )
    })
  })

  it('should redirect to /accueil page if user has at least one offerer name', async () => {
    // Mock offerer names with at least one entry
    vi.mocked(api.listOfferersNames).mockResolvedValue({
      offerersNames: [{ id: 1, name: 'Test Offerer', allowedOnAdage: false }],
    })

    renderUseRedirectLoggedUser('/')

    // Wait for the effect to run
    await vi.waitFor(() => {
      expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
      expect(mockNavigate).toHaveBeenCalledWith('/accueil?')
    })
  })

  it('should redirect user to /offers page if we have a "de" param in query string', async () => {
    // Mock offerer names with at least one entry
    vi.mocked(api.listOfferersNames).mockResolvedValue({
      offerersNames: [{ id: 1, name: 'Test Offerer', allowedOnAdage: false }],
    })

    renderUseRedirectLoggedUser('/?de=%2Foffers')

    // Wait for the effect to run
    await vi.waitFor(() => {
      expect(api.listOfferersNames).toHaveBeenCalledTimes(1)
      expect(mockNavigate).toHaveBeenCalledWith('/offers')
    })
  })
})

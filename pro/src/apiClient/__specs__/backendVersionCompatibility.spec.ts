import {
  BACKEND_VERSION_MISMATCH_EVENT,
  notifyIfBackendVersionChanged,
} from '../backendVersionCompatibility'

vi.mock('@/commons/utils/config', () => ({
  API_URL: 'https://backend.example',
  VITE_APP_VERSION: 'current-version',
  IS_DEV: false,
}))

describe('notifyIfBackendVersionChanged', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  it.each([404, 405, 501])(
    'should check the backend version for an HTTP %s error',
    async (status) => {
      vi.mocked(fetch).mockResolvedValue({
        ok: true,
        text: async () => 'next-version',
      } as Response)
      const mismatchEventSpy = vi.spyOn(window, 'dispatchEvent')

      await notifyIfBackendVersionChanged(new Response(null, { status }))

      expect(fetch).toHaveBeenCalledExactlyOnceWith(
        'https://backend.example/health/api',
        { cache: 'no-store' }
      )
      expect(mismatchEventSpy).toHaveBeenCalledWith(
        expect.objectContaining({ type: BACKEND_VERSION_MISMATCH_EVENT })
      )
    }
  )

  it.each([400, 403, 422, 500])(
    'should not check the backend version for an HTTP %s error',
    async (status) => {
      const mismatchEventSpy = vi.spyOn(window, 'dispatchEvent')

      await notifyIfBackendVersionChanged(new Response(null, { status }))

      expect(fetch).not.toHaveBeenCalled()
      expect(mismatchEventSpy).not.toHaveBeenCalled()
    }
  )

  it('should not emit an event when backend and frontend versions match', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      text: async () => 'current-version',
    } as Response)
    const mismatchEventSpy = vi.spyOn(window, 'dispatchEvent')

    await notifyIfBackendVersionChanged(new Response(null, { status: 404 }))

    expect(mismatchEventSpy).not.toHaveBeenCalled()
  })

  it('should not emit an event when the health check is not successful', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      text: async () => 'next-version',
    } as Response)
    const mismatchEventSpy = vi.spyOn(window, 'dispatchEvent')

    await notifyIfBackendVersionChanged(new Response(null, { status: 404 }))

    expect(mismatchEventSpy).not.toHaveBeenCalled()
  })

  it('should keep the original API error flow when the health check fails', async () => {
    vi.mocked(fetch).mockRejectedValue(new Error('Network error'))
    const mismatchEventSpy = vi.spyOn(window, 'dispatchEvent')

    await expect(
      notifyIfBackendVersionChanged(new Response(null, { status: 404 }))
    ).resolves.toBeUndefined()
    expect(mismatchEventSpy).not.toHaveBeenCalled()
  })
})

import { API_URL, IS_DEV, VITE_APP_VERSION } from '@/commons/utils/config'

export const BACKEND_VERSION_MISMATCH_EVENT = 'backend-version-mismatch'

const BACKEND_VERSION_MISMATCH_CANDIDATE_STATUSES = new Set([404, 405, 501])

export async function notifyIfBackendVersionChanged(
  response: Response
): Promise<void> {
  if (
    !VITE_APP_VERSION ||
    IS_DEV ||
    !BACKEND_VERSION_MISMATCH_CANDIDATE_STATUSES.has(response.status)
  ) {
    return
  }

  try {
    const healthResponse = await fetch(`${API_URL}/health/api`, {
      cache: 'no-store',
    })
    const backendVersion = (await healthResponse.text()).trim()

    if (healthResponse.ok && backendVersion !== VITE_APP_VERSION) {
      window.dispatchEvent(new Event(BACKEND_VERSION_MISMATCH_EVENT))
    }
  } catch {
    // Keep the original API error when the health check cannot be reached.
  }
}

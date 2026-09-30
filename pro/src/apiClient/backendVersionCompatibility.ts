import {
  API_URL,
  IS_DEV,
  IS_TESTING,
  VITE_APP_VERSION,
} from '@/commons/utils/config'

export const BACKEND_VERSION_HIGHER_EVENT = 'backend-version-higher'
export const BACKEND_VERSION_LOWER_EVENT = 'backend-version-lower'

const BACKEND_VERSION_MISMATCH_CANDIDATE_STATUSES = new Set([404, 405, 501])

export type VersionComparison = 'higher' | 'lower' | 'equal'

const compareVersions = (
  versionA: string,
  versionB: string
): VersionComparison => {
  const partsA = versionA.split('.').map(Number)
  const partsB = versionB.split('.').map(Number)

  for (let index = 0; index < Math.max(partsA.length, partsB.length); index++) {
    const difference = (partsA[index] ?? 0) - (partsB[index] ?? 0)
    if (difference !== 0) {
      return difference > 0 ? 'higher' : 'lower'
    }
  }

  return 'equal'
}

export async function notifyIfBackendVersionChanged(
  response: Response
): Promise<void> {
  if (
    !VITE_APP_VERSION ||
    IS_DEV ||
    IS_TESTING ||
    !BACKEND_VERSION_MISMATCH_CANDIDATE_STATUSES.has(response.status)
  ) {
    return
  }

  try {
    const healthResponse = await fetch(`${API_URL}/health/api`, {
      cache: 'no-store',
    })
    const backendVersion = (await healthResponse.text()).trim()

    if (!healthResponse.ok) {
      return
    }

    const versionComparison = compareVersions(backendVersion, VITE_APP_VERSION)

    if (versionComparison === 'higher') {
      window.dispatchEvent(new Event(BACKEND_VERSION_HIGHER_EVENT))
    } else if (versionComparison === 'lower') {
      window.dispatchEvent(new Event(BACKEND_VERSION_LOWER_EVENT))
    }
  } catch {
    // Keep the original API error when the health check cannot be reached.
  }
}

import { useEffect, useState } from 'react'

import {
  BACKEND_VERSION_HIGHER_EVENT,
  BACKEND_VERSION_LOWER_EVENT,
} from '@/apiClient/api'
import type { VersionComparison } from '@/apiClient/backendVersionCompatibility'

export const useCheckBackendVersion = (): VersionComparison => {
  const [backendVersionComparison, setBackendVersionComparison] =
    useState<VersionComparison>('equal')

  useEffect(() => {
    const handleBackendVersionHigher = () =>
      setBackendVersionComparison('higher')
    const handleBackendVersionLower = () => setBackendVersionComparison('lower')

    window.addEventListener(
      BACKEND_VERSION_HIGHER_EVENT,
      handleBackendVersionHigher
    )

    window.addEventListener(
      BACKEND_VERSION_LOWER_EVENT,
      handleBackendVersionLower
    )

    return () => {
      window.removeEventListener(
        BACKEND_VERSION_HIGHER_EVENT,
        handleBackendVersionHigher
      )
      window.removeEventListener(
        BACKEND_VERSION_LOWER_EVENT,
        handleBackendVersionLower
      )
    }
  }, [])

  return backendVersionComparison
}

import { useEffect, useState } from 'react'

import { BACKEND_VERSION_MISMATCH_EVENT } from '@/apiClient/api'

export const useCheckBackendVersion = (): boolean => {
  const [hasBackendVersionMismatch, setHasBackendVersionMismatch] =
    useState(false)

  useEffect(() => {
    const handleBackendVersionMismatch = () => {
      setHasBackendVersionMismatch(true)
    }

    window.addEventListener(
      BACKEND_VERSION_MISMATCH_EVENT,
      handleBackendVersionMismatch
    )

    return () =>
      window.removeEventListener(
        BACKEND_VERSION_MISMATCH_EVENT,
        handleBackendVersionMismatch
      )
  }, [])

  return hasBackendVersionMismatch
}

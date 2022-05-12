import React, { useEffect, useState } from 'react'

import { getOffererNamesAdapter } from 'core/Offerers/adapters'
import { TOffererName } from 'core/Offerers/types'

const useOffererNames = (): {
  isLoading: boolean
  offererNames: TOffererName[]
  error: string
} => {
  const [offererNames, setOffererNames] = useState<TOffererName[]>([])
  const [error, setError] = useState<string>('')
  const [isLoading, setIsLoading] = useState<boolean>(true)
  useEffect(() => {
    async function loadData() {
      const response = await getOffererNamesAdapter()
      if (response.isOk) {
        setOffererNames(response.payload)
      } else {
        setError(response.message)
      }

      setIsLoading(false)
    }
    if (isLoading) {
      loadData()
    }
  }, [isLoading])

  return { isLoading, offererNames, error }
}

export default useOffererNames

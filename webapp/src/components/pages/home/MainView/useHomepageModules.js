import { parse } from 'query-string'
import { useEffect, useState } from 'react'

import { fetchHomepage } from '../../../../vendor/contentful/contentful'

const useHomepageModules = history => {
  const [modules, setModules] = useState([])
  const [isError, setIsError] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const parsedSearch = parse(history.location.search)
    setIsError(false)
    setIsLoading(true)

    fetchHomepage({ entryId: parsedSearch ? parsedSearch.entryId : '' })
      .then(setModules)
      .catch(() => setIsError(true))
      .then(() => setIsLoading(false))
  }, [history.location.search])

  return {
    modules,
    isError,
    isLoading,
  }
}

export default useHomepageModules

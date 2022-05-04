import { useCallback, useMemo } from 'react'
import { useHistory, useLocation } from 'react-router-dom'

import {
  translateApiParamsToQueryParams,
  translateQueryParamsToApiParams,
} from 'utils/translate'

const useFrenchQuery = () => {
  const location = useLocation()
  const history = useHistory()

  const frenchQueryParams = useMemo(
    () => Object.fromEntries(new URLSearchParams(location.search)),
    [location]
  )
  const englishQueryParams = useMemo(
    () => translateQueryParamsToApiParams(frenchQueryParams),
    [frenchQueryParams]
  )

  const setQuery = useCallback(
    newEnglishQueryParams => {
      const frenchQueryParams = translateApiParamsToQueryParams(
        newEnglishQueryParams
      )
      const frenchQueryString = new URLSearchParams(
        frenchQueryParams
      ).toString()
      history.push(`${location.pathname}?${frenchQueryString}`)
    },
    [history, location.pathname]
  )

  return [englishQueryParams, setQuery]
}

export default useFrenchQuery

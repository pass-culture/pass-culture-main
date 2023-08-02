import React, { useCallback, useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'

import { Banner } from 'ui-kit'
import { parse, stringify } from 'utils/query-string'

export const DomainNameBanner = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const queryParams = parse(location.search)
  const [shouldDisplayBanner, setShouldDisplayBanner] = useState(false)

  useEffect(() => {
    if (!shouldDisplayBanner && queryParams['redirect']) {
      setShouldDisplayBanner(true)
    }
  }, [queryParams, shouldDisplayBanner])

  const closeBanner = useCallback(() => {
    delete queryParams['redirect']
    navigate({ search: stringify(queryParams) }, { replace: true })

    setShouldDisplayBanner(false)
  }, [history, queryParams])

  if (!shouldDisplayBanner) {
    return null
  }

  return (
    <Banner
      className="domain-name-banner"
      closable
      handleOnClick={closeBanner}
      type="attention"
    >
      Notre nom de domaine évolue ! Vous avez été automatiquement redirigé
      vers&nbsp;
      <strong>https://passculture.pro</strong>
    </Banner>
  )
}

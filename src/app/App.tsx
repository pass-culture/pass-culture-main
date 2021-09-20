import * as React from "react"
import { useCallback, useEffect, useState } from "react"

import "@fontsource/barlow"
import { UnauthenticatedError } from "app/components/UnauthenticatedError/UnauthenticatedError"
import * as pcapi from "repository/pcapi/pcapi"
import { Role, VenueFilterType } from "utils/types"

import { AppLayout } from "./AppLayout"
import { LoaderPage } from "./components/LoaderPage/LoaderPage"

export const App = (): JSX.Element => {
  const [userRole, setUserRole] = useState<Role>(Role.unauthenticated)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [venueFilter, setVenueFilter] = useState<VenueFilterType | null>(null)

  useEffect(() => {
    pcapi
      .authenticate()
      .then((userRole) => setUserRole(userRole))
      .then(() => {
        const params = new URLSearchParams(window.location.search)
        const siret = params.get("siret")
        if (siret) {
          return pcapi
            .getVenueBySiret(siret)
            .then((venueFilter) => setVenueFilter(venueFilter))
            .catch()
        }
      })
      .catch(() => setUserRole(Role.unauthenticated))
      .finally(() => setIsLoading(false))
  }, [])

  const removeVenueFilter = useCallback(() => setVenueFilter(null), [])

  if (isLoading) {
    return <LoaderPage />
  }

  return (
    <>
      {[Role.readonly, Role.redactor].includes(userRole) && (
        <AppLayout
          removeVenueFilter={removeVenueFilter}
          userRole={userRole}
          venueFilter={venueFilter}
        />
      )}
      {userRole === Role.unauthenticated && <UnauthenticatedError />}
    </>
  )
}

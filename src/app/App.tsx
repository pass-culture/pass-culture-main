import * as React from "react"
import { useEffect, useState } from "react"

import "@fontsource/barlow"
import { UnauthenticatedError } from "app/components/UnauthenticatedError/UnauthenticatedError"
import * as pcapi from "repository/pcapi/pcapi"
import { Role } from "utils/types"

import { AppLayout } from "./AppLayout"
import { LoaderPage } from "./components/LoaderPage/LoaderPage"

export const App = (): JSX.Element => {
  const [userRole, setUserRole] = useState<Role>(Role.authenticating)

  useEffect(() => {
    pcapi
      .authenticate()
      .then((userRole) => setUserRole(userRole))
      .catch(() => setUserRole(Role.unauthenticated))
  }, [])

  return (
    <>
      {[Role.readonly, Role.redactor].includes(userRole) && (
        <AppLayout userRole={userRole} />
      )}
      {userRole === Role.unauthenticated && <UnauthenticatedError />}
      {userRole === Role.authenticating && <LoaderPage />}
    </>
  )
}

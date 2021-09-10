import * as React from "react"
import { useEffect, useState } from "react"

import { UnauthenticatedError } from "app/components/UnauthenticatedError/UnauthenticatedError"
import * as pcapi from "repository/pcapi/pcapi"

import AppLayout from "./AppLayout"

const App = (): JSX.Element => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)

  useEffect(() => {
    pcapi
      .authenticate()
      .then(() => setIsAuthenticated(true))
      .catch(() => setIsAuthenticated(false))
  }, [])

  return (
    <>
      {isAuthenticated === true && <AppLayout />}
      {isAuthenticated === false && <UnauthenticatedError />}
    </>
  )
}

export default App

import "./App.scss"
import * as React from "react"
import { useEffect, useState } from "react"

import * as pcapi from "repository/pcapi/pcapi"

import { OffersSearch } from "./components/OffersSearch/OffersSearch"

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
      <header>
        <h1>
          pass Culture
        </h1>
      </header>
      <main>
        {isAuthenticated === true && <OffersSearch />}
        {isAuthenticated === false && (
          <h2>
            {"Vous n'êtes pas autorisé à accéder à cette page"}
          </h2>
        )}
        {isAuthenticated === undefined && (
          <h2>
            En cours de connexion...
          </h2>
        )}
      </main>
      <footer />
    </>
  )
}

export default App

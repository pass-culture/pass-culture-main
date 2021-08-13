import "./App.scss"
import * as React from "react"

import * as pcapi from "repository/pcapi/pcapi"
import {useEffect, useState} from "react";

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean|null>(null)

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
        {isAuthenticated === true && (
          <>
            <h2>
              Bienvenue
            </h2>
            <h3>
              Vos offres
            </h3>
            <div>
              Vous trouverez ici la liste des offres disponibles.
            </div>
          </>
        )}
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
      <footer>
        Mentions légales
      </footer>
    </>
  )
}

export default App

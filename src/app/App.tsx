import "./App.scss"
import "@elastic/react-search-ui-views/lib/styles/styles.css"
import { SearchProvider, Results, SearchBox } from "@elastic/react-search-ui"
import { Layout } from "@elastic/react-search-ui-views"
import AppSearchAPIConnector from "@elastic/search-ui-app-search-connector"
import * as React from "react"
import {useEffect, useState} from "react"

import * as pcapi from "repository/pcapi/pcapi"
import { REACT_APP_APP_SEARCH_ENDPOINT, REACT_APP_APP_SEARCH_KEY } from "utils/config"

const connector = new AppSearchAPIConnector({
  searchKey: REACT_APP_APP_SEARCH_ENDPOINT,
  engineName: "offers",
  endpointBase: REACT_APP_APP_SEARCH_KEY,
})

const App = ():JSX.Element => {
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
        <SearchProvider
          config={{
            apiConnector: connector
          }}
        >
          <div className="App">
            <Layout
              bodyContent={(
                <Results
                  titleField="title"
                  urlField="nps_link"
                />
              )}
              header={<SearchBox />}
            />
          </div>
        </SearchProvider>
      </main>
      <footer>
        Mentions légales
      </footer>
    </>
  )
}

export default App

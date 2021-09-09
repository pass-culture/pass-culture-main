import "./App.scss"
import "@elastic/react-search-ui-views/lib/styles/styles.css"
import {
  SearchProvider,
  SearchBox,
  WithSearch,
} from "@elastic/react-search-ui"
import AppSearchAPIConnector from "@elastic/search-ui-app-search-connector"
import * as React from "react"
import { useEffect, useState, useCallback } from "react"

import * as pcapi from "repository/pcapi/pcapi"
import { APP_SEARCH_ENDPOINT, APP_SEARCH_KEY } from "utils/config"
import { RESULT_FIELDS } from "utils/search"

import Offers from "./components/Offers"

const connector = new AppSearchAPIConnector({
  searchKey: APP_SEARCH_KEY,
  engineName: "offers",
  endpointBase: APP_SEARCH_ENDPOINT,
})

const configurationOptions = {
  searchQuery: {
    result_fields: RESULT_FIELDS,
    filters: [{ field: "is_educational", values: [1] }],
  },
}

const App = (): JSX.Element => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)

  useEffect(() => {
    pcapi
      .authenticate()
      .then(() => setIsAuthenticated(true))
      .catch(() => setIsAuthenticated(false))
  }, [])

  const mapContextToProps = useCallback(
    ({
      autocompletedResults,
      autocompletedSuggestions,
      trackAutocompleteClickThrough,
      searchTerm,
      setSearchTerm,
      results,
    }) => ({
      autocompletedResults,
      autocompletedSuggestions,
      trackAutocompleteClickThrough,
      searchTerm,
      setSearchTerm,
      results,
    }),
    []
  )

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
            apiConnector: connector,
            ...configurationOptions,
          }}
        >
          <WithSearch mapContextToProps={mapContextToProps}>
            {({
              autocompletedResults,
              autocompletedSuggestions,
              trackAutocompleteClickThrough,
              searchTerm,
              setSearchTerm,
              results,
            }) => {
              return (
                <>
                  <SearchBox
                    autocompletedResults={autocompletedResults}
                    autocompletedSuggestions={autocompletedSuggestions}
                    searchTerm={searchTerm}
                    setSearchTerm={setSearchTerm}
                    trackAutocompleteClickThrough={
                      trackAutocompleteClickThrough
                    }
                  />
                  <Offers results={results} />
                </>
              )
            }}
          </WithSearch>
        </SearchProvider>
      </main>
      <footer>
        Mentions légales
      </footer>
    </>
  )
}

export default App

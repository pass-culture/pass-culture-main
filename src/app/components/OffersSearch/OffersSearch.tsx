import "./OffersSearch.scss"
import "@elastic/react-search-ui-views/lib/styles/styles.css"
import {
  SearchBox,
  SearchProvider,
  WithSearch,
} from "@elastic/react-search-ui"
import AppSearchAPIConnector from "@elastic/search-ui-app-search-connector"
import * as React from "react"
import { useCallback, useEffect, useState } from "react"

import { VenueFilterStatus } from "app/components/OffersSearch/VenueFilterStatus/VenueFilterStatus"
import { APP_SEARCH_ENDPOINT, APP_SEARCH_KEY } from "utils/config"
import { RESULT_FIELDS } from "utils/search"
import { Role, VenueFilterType } from "utils/types"

import { Offers } from "./Offers/Offers"

const connector = new AppSearchAPIConnector({
  searchKey: APP_SEARCH_KEY,
  engineName: "offers-meta",
  endpointBase: APP_SEARCH_ENDPOINT,
})

const configurationOptions = {
  trackUrlState: false,
  alwaysSearchOnInitialLoad: true,
}

export const OffersSearch = ({
  userRole,
  removeVenueFilter,
  venueFilter,
}: {
  userRole: Role;
  removeVenueFilter: () => void;
  venueFilter: VenueFilterType | null;
}): JSX.Element => {
  const baseSearchQuery = {
    result_fields: RESULT_FIELDS,
    filters: [{ field: "is_educational", values: [1] }],
  }
  if (venueFilter) {
    baseSearchQuery.filters.push({
      field: "venue_id",
      values: [venueFilter.id],
    })
  }
  const [searchQuery, setSearchQuery] = useState({ ...baseSearchQuery })

  useEffect(() => {
    if (
      !venueFilter &&
      searchQuery.filters.find((filter) => filter.field === "venue_id")
    ) {
      setSearchQuery((currentSearchQuery) => ({
        ...currentSearchQuery,
        filters: currentSearchQuery.filters.filter(
          (filter) => filter.field !== "venue_id"
        ),
      }))
    }
  }, [searchQuery.filters, venueFilter])

  const mapContextToProps = useCallback(
    ({
      autocompletedResults,
      autocompletedSuggestions,
      trackAutocompleteClickThrough,
      searchTerm,
      setSearchTerm,
      results,
      isLoading,
      wasSearched,
    }) => ({
      autocompletedResults,
      autocompletedSuggestions,
      trackAutocompleteClickThrough,
      searchTerm,
      setSearchTerm,
      results,
      isLoading,
      wasSearched,
    }),
    []
  )

  const inputView = useCallback(
    ({ getAutocomplete, getInputProps, getButtonProps }) => (
      <>
        <div className="sui-search-box__wrapper">
          <input
            {...getInputProps({
              placeholder:
                "Nom de l'offre, du lieu ou de la catégorie (films, visites, conférences, spectacles, cours, musique)",
            })}
          />
          {getAutocomplete()}
        </div>
        <input
          {...getButtonProps({
            value: "Rechercher",
            className: "search-button",
          })}
        />
      </>
    ),
    []
  )

  return (
    <>
      <h2>
        Rechercher une offre
      </h2>
      <SearchProvider
        config={{
          apiConnector: connector,
          searchQuery,
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
            isLoading,
            wasSearched,
          }) => {
            return (
              <>
                <SearchBox
                  autocompletedResults={autocompletedResults}
                  autocompletedSuggestions={autocompletedSuggestions}
                  inputView={inputView}
                  searchTerm={searchTerm}
                  setSearchTerm={setSearchTerm}
                  trackAutocompleteClickThrough={trackAutocompleteClickThrough}
                />
                <div className="search-results">
                  {venueFilter && (
                    <VenueFilterStatus
                      removeFilter={removeVenueFilter}
                      venueFilter={venueFilter}
                    />
                  )}
                  <Offers
                    isAppSearchLoading={isLoading}
                    results={results}
                    userRole={userRole}
                    wasFirstSearchLaunched={wasSearched}
                  />
                </div>
              </>
            )
          }}
        </WithSearch>
      </SearchProvider>
    </>
  )
}

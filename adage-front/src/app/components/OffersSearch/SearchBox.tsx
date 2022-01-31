import './SearchBox.scss'
import React, { useCallback } from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'

import { ReactComponent as MagnifyingGlassIcon } from 'assets/magnifying-glass.svg'

export const SearchBoxComponent = ({
  query,
  setQuery,
  refine,
}: {
  query: string
  setQuery: (query: string) => void
  refine: SearchBoxProvided['refine']
}): React.ReactElement => {
  const onSubmit = useCallback(
    event => {
      event.preventDefault()
      refine(query)
    },
    [query, refine]
  )

  return (
    <form className="search-wrapper" onSubmit={onSubmit}>
      <MagnifyingGlassIcon className="search-icon" />
      <input
        className="search-box"
        onChange={e => setQuery(e.target.value)}
        placeholder="Nom de l'offre, du lieu ou de la catégorie (films, visites, conférences, spectacles, cours, musique)"
        type="search"
        value={query}
      />
    </form>
  )
}

export const SearchBox = SearchBoxComponent

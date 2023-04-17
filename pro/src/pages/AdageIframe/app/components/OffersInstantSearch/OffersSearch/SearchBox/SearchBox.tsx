import './SearchBox.scss'
import React, { useCallback, useContext } from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'

import { ReactComponent as SearchIco } from 'icons/search-ico.svg'
import { AlgoliaQueryContext } from 'pages/AdageIframe/app/providers'

export const SearchBoxComponent = ({
  refine,
}: {
  refine: SearchBoxProvided['refine']
}): React.ReactElement => {
  const { query, setQuery, setQueryTag } = useContext(AlgoliaQueryContext)

  const onSubmit = useCallback(
    (event: React.FormEvent) => {
      event.preventDefault()
      setQueryTag(query)
      refine(query)
    },
    [query, refine, setQueryTag]
  )

  return (
    <form className="search-wrapper" onSubmit={onSubmit}>
      <SearchIco className="search-icon" />
      <input
        className="search-box"
        onChange={e => setQuery(e.target.value)}
        placeholder="Nom de l’offre ou du partenaire culturel"
        type="search"
        value={query}
      />
    </form>
  )
}

export const SearchBox = SearchBoxComponent

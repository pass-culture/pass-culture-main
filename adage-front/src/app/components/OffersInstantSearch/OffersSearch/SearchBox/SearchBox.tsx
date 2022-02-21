import './SearchBox.scss'
import React, { useCallback, useContext } from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'

import { AlgoliaQueryContext } from 'app/providers/AlgoliaQueryContextProvider'
import { ReactComponent as MagnifyingGlassIcon } from 'assets/magnifying-glass.svg'

import { placeholder } from './constants'

export const SearchBoxComponent = ({
  refine,
}: {
  refine: SearchBoxProvided['refine']
}): React.ReactElement => {
  const { query, setQuery, setQueryTag } = useContext(AlgoliaQueryContext)

  const onSubmit = useCallback(
    event => {
      event.preventDefault()
      setQueryTag(query)
      refine(query)
    },
    [query, refine, setQueryTag]
  )

  return (
    <form className="search-wrapper" onSubmit={onSubmit}>
      <MagnifyingGlassIcon className="search-icon" />
      <input
        className="search-box"
        onChange={e => setQuery(e.target.value)}
        placeholder={placeholder}
        type="search"
        value={query}
      />
    </form>
  )
}

export const SearchBox = SearchBoxComponent

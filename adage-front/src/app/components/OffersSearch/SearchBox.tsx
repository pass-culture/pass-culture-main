import "./SearchBox.scss"
import React, { useCallback } from "react"
import { connectSearchBox } from "react-instantsearch-core"

export const SearchBoxComponent = ({
  currentRefinement,
  refine,
}: {
  currentRefinement: string;
  refine: (e: string) => void;
}): React.ReactElement => {
  const onSubmit = useCallback((event) => {
    event.preventDefault()
  }, [])

  const onChange = useCallback(
    (event) => {
      refine(event.currentTarget.value)
    },
    [refine]
  )

  return (
    <form
      className="search-wrapper"
      onSubmit={onSubmit}
    >
      <input
        className="search-box"
        onChange={onChange}
        placeholder="Nom de l'offre, du lieu ou de la catégorie (films, visites, conférences, spectacles, cours, musique)"
        type="search"
        value={currentRefinement}
      />
      <button
        className="search-button"
        type="submit"
      >
        Rechercher
      </button>
    </form>
  )
}

export const SearchBox = connectSearchBox(SearchBoxComponent)

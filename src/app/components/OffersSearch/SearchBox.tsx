import React, { useCallback } from "react"
import { connectSearchBox } from "react-instantsearch-core"

const SearchBoxComponent = ({
  currentRefinement,
  refine,
}: {
  currentRefinement: string;
  refine: (e: string) => void;
}) => {
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
    <form onSubmit={onSubmit}>
      <input
        onChange={onChange}
        placeholder="Nom de l'offre, du lieu ou de la catégorie (films, visites, conférences, spectacles, cours, musique)"
        type="search"
        value={currentRefinement}
      />
      <button type="submit">
        Rechercher
      </button>
    </form>
  )
}

export const SearchBox = connectSearchBox(SearchBoxComponent)

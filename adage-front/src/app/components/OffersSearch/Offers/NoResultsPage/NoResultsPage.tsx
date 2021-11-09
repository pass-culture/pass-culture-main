import "./NoResultsPage.scss"
import React from "react"

import { ReactComponent as NoResultsIcon } from "./assets/no-results-icon.svg"

export const NoResultsPage = (): JSX.Element => (
  <div className="no-results">
    <NoResultsIcon />
    <p>
      Aucun résultat trouvé pour cette recherche.
    </p>
  </div>
)

import React from 'react'

import strokeNoResultIcon from 'icons/stroke-no-result.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NoResultsPage.module.scss'

interface NoResultsPageProps {
  query?: string
}

export const NoResultsPage = ({ query }: NoResultsPageProps): JSX.Element => {
  const noResultText = !query ? (
    'Nous n’avons trouvé aucune offre publiée'
  ) : (
    <>
      Nous n’avons trouvé aucune offre publiée pour :
      <span className={styles['no-results-text-query-container']}>
        “<span className={styles['no-results-text-query']}>{query}</span>”
      </span>
    </>
  )

  const noResultSuggestionText = !query
    ? 'Votre recherche semble trop ciblée... Réessayez en supprimant un ou plusieurs filtres.'
    : 'Vérifiez l’orthographe des termes, essayez d’autres mot-clés, ou modifiez les filtres pour trouver des résultats.'

  return (
    <div className={styles['no-results']}>
      <SvgIcon
        src={strokeNoResultIcon}
        alt=""
        className={styles['no-results-icon']}
        width="156"
      />
      <p className={styles['no-results-text']}>{noResultText}</p>
      <p className={styles['no-results-suggestion-text']}>
        {noResultSuggestionText}
      </p>
    </div>
  )
}

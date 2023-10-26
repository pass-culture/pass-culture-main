import React from 'react'

import styles from './NoResultsPage.module.scss'

interface NoResultsPageProps {
  query?: string
}

export const NoResultsPage = ({ query }: NoResultsPageProps): JSX.Element => {
  const noResultText = !query ? (
    'Nous n’avons trouvé aucune offre publiée'
  ) : (
    <>
      <span className={styles['no-results-text-query-container']}>
        “<span className={styles['no-results-text-query']}>{query}</span>”
      </span>{' '}
      n’a pas d’offres disponibles pour le moment
    </>
  )

  const noResultSuggestionText = !query
    ? 'Votre recherche semble trop ciblée... Réessayez en supprimant un ou plusieurs filtres.'
    : 'Vérifiez l’orthographe des termes, essayez d’autres mot-clés, ou modifiez les filtres pour trouver des résultats.'

  return (
    <div className={styles['no-results']}>
      <p className={styles['no-results-text']}>{noResultText}</p>
      <p className={styles['no-results-suggestion']}>
        {noResultSuggestionText}
      </p>
    </div>
  )
}

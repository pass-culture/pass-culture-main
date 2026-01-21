import type { VenueResponse } from '@/apiClient/adage'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'

import styles from './NoResultsPage.module.scss'

interface NoResultsPageProps {
  query?: string
  venue?: VenueResponse | null
}

export const NoResultsPage = ({
  query,
  venue,
}: NoResultsPageProps): JSX.Element => {
  const noResultText = !query ? (
    'Nous n’avons trouvé aucune offre publiée'
  ) : (
    <>
      Nous n’avons trouvé aucune offre publiée pour :{' '}
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
      <p className={styles['no-results-text']}>{noResultText}</p>
      <p className={styles['no-results-suggestion']}>
        {!venue && noResultSuggestionText}
      </p>
      {venue?.adageId && (
        <Button
          as="a"
          isExternal
          to={`${document.referrer}adage/ressource/partenaires/id/${venue.adageId}`}
          opensInNewTab
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          icon={fullLinkIcon}
          label="Voir la fiche du partenaire"
        />
      )}
    </div>
  )
}

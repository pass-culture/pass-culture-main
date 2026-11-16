import { useEffect } from 'react'
import { useInstantSearch } from 'react-instantsearch'

import { useSnackBar } from '@/commons/hooks/useSnackBar'

export function AlgoliaSearchErrorListener() {
  const { status, error } = useInstantSearch({ catchError: true })
  const snackBar = useSnackBar()

  useEffect(() => {
    if (status === 'error' && error) {
      snackBar.error(
        'Une erreur est survenue lors de la recherche. Veuillez réessayer.'
      )
    }
  }, [status, error, snackBar])

  return null
}

import { useLocation } from 'react-router'

import { ErrorLayout } from '@/app/App/layouts/ErrorLayout/ErrorLayout'
import stroke404Icon from '@/icons/stroke-404.svg'

export const NotFound = () => {
  const { state } = useLocation()

  return (
    <ErrorLayout
      mainHeading="Oh non !"
      paragraph={
        state?.from === 'offer'
          ? 'Cette offre n’existe pas ou a été supprimée.'
          : 'Cette page n’existe pas.'
      }
      errorIcon={stroke404Icon}
    />
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = NotFound

import stroke404Icon from 'icons/stroke-404.svg'
import { useLocation } from 'react-router'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NotFound.module.scss'

type NotFoundProps = {
  redirect?: string
}

export const NotFound = ({ redirect = '/accueil' }: NotFoundProps) => {
  const { state } = useLocation()

  return (
    <main className={styles['not-found']} id="content">
      <div className={styles['not-found-content']}>
        <SvgIcon
          src={stroke404Icon}
          alt=""
          className={styles['no-match-icon']}
          width="350"
        />
        <h1 className={styles['title']}>Oh non !</h1>
        <p>
          {state?.from === 'offer'
            ? 'Cette offre n’existe pas ou a été supprimée.'
            : 'Cette page n’existe pas.'}
        </p>
        <ButtonLink
          className={styles['nm-redirection-link']}
          variant={ButtonVariant.SECONDARY}
          to={redirect}
        >
          Retour à la page d’accueil
        </ButtonLink>
      </div>
    </main>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = NotFound

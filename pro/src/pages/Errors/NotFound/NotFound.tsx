import stroke404Icon from 'icons/stroke-404.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NotFound.module.scss'

type NotFoundProps = {
  redirect?: string
}

export const NotFound = ({ redirect = '/accueil' }: NotFoundProps) => (
  <main className={styles['no-match']} id="content">
    <SvgIcon
      src={stroke404Icon}
      alt=""
      className={styles['no-match-icon']}
      width="350"
    />
    <h1>Oh non !</h1>
    <p>Cette page n’existe pas.</p>
    <ButtonLink
      className={styles['nm-redirection-link']}
      variant={ButtonVariant.SECONDARY}
      link={{ to: redirect, isExternal: false }}
    >
      Retour à la page d’accueil
    </ButtonLink>
  </main>
)

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = NotFound

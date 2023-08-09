import React from 'react'
import { Link } from 'react-router-dom'

import stroke404Icon from 'icons/stroke-404.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NotFound.module.scss'
interface Props {
  redirect?: string
}

const NotFound = ({ redirect = '/accueil' }: Props) => (
  <main className={styles['no-match']} id="content">
    <SvgIcon
      src={stroke404Icon}
      alt=""
      className={styles['no-match-icon']}
      viewBox="0 0 308 194"
      width="350"
    />
    <h1>Oh non !</h1>
    <p>Cette page n’existe pas.</p>
    <Link className={styles['nm-redirection-link']} to={redirect}>
      Retour à la page d’accueil
    </Link>
  </main>
)

export default NotFound

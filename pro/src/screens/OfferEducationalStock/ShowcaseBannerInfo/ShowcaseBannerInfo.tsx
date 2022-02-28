import React from 'react'

import Icon from 'components/layout/Icon'

import styles from './ShowcaseBannerInfo.module.scss'

const ShowcaseBannerInfo = (): JSX.Element => (
  <div className={styles['showcase-banner-info']}>
    <b>Dans ce cas là :</b>
    <br />
    <br />
    <p>
      1) À sa création, votre offre sera visible sur ADAGE
      <br />
      2) L’enseignant pourra vous contacter et vous discuterez ensemble des
      détails de l'offre
      <br />
      3) Après un accord mutuel, vous pourrez revenir éditer cette offre et y
      ajouter les éléments de date et prix
      <br />
      4) Une fois l'offre complétée elle sera préréservable sur ADAGE par
      l'enseignant
    </p>
    <br />
    <p>
      <a
        className="bi-link tertiary-link"
        href="https://aide.passculture.app/hc/fr/articles/4412172981020"
        rel="noopener noreferrer"
        target="_blank"
      >
        <Icon svg="ico-external-site" />
        Consultez l’article “Comment créer une offre sans date ni prix à
        destination d’un établissement scolaire ?”
      </a>
    </p>
  </div>
)

export default ShowcaseBannerInfo

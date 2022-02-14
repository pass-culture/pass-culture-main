import React from 'react'

import styles from './ShowcaseBannerInfo.module.scss'

const ShowcaseBannerInfo = (): JSX.Element => (
  <div className={styles['showcase-banner-info']}>
    <b>Dans ce cas là :</b>
    <br />
    <br />
    <p>
      1) À sa création, votre offre sera visible sur Adage
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
  </div>
)

export default ShowcaseBannerInfo

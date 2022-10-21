import React from 'react'

import Icon from 'components/layout/Icon'
import useActiveFeature from 'hooks/useActiveFeature'
import { Banner } from 'ui-kit'

import styles from './ShowcaseBannerInfo.module.scss'

const ShowcaseBannerInfo = (): JSX.Element => {
  const isOfferDuplicationEnabled = useActiveFeature(
    'WIP_CREATE_COLLECTIVE_OFFER_FROM_TEMPLATE'
  )

  return isOfferDuplicationEnabled ? (
    <Banner
      type="notification-info"
      links={[
        {
          isExternal: true,
          href: 'https://aide.passculture.app/hc/fr/articles/4416082284945',
          linkTitle:
            'Consultez l’article “Quel est le cycle de vie de mon offre collective, de sa création à son remboursement ?”',
        },
      ]}
    >
      1) À sa création, votre offre vitrine sera visible sur ADAGE, la
      plateforme des enseignants
      <br />
      2) L’enseignant vous contactera pour discuter des détails de l'offre
      <br />
      3) Vous créerez une offre réservable en complétant la date, le prix et
      l’établissement vus avec l’enseignant
      <br />
      4) Une fois cette nouvelle offre publiée, elle sera préréservable sur
      ADAGE par l'enseignant
      <br />
    </Banner>
  ) : (
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
}

export default ShowcaseBannerInfo

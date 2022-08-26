import React from 'react'

import Banner from 'ui-kit/Banners/Banner'

import styles from './BannerPendingEmailValidation.module.scss'

interface Props {
  email: string
}

const BannerPendingEmailValidation = ({ email }: Props): JSX.Element => (
  <Banner
    links={[
      {
        href: 'https://aide.passculture.app/hc/fr/articles/4458607720732--Acteurs-Culturels-Comment-assurer-la-s%C3%A9curit%C3%A9-de-votre-compte-',
        linkTitle: "Je n'ai pas reçu le lien de confirmation",
      },
    ]}
    type="attention"
  >
    Pour valider ce changement, un lien de confirmation valable 24 heures vous a
    été envoyé à l’adresse :
    <span className={styles['banner-email-adress']}> {email}</span>
  </Banner>
)

export default BannerPendingEmailValidation

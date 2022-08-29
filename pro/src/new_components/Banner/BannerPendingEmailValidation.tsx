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
        href: 'https://aide.passculture.app/hc/fr/articles/5723750427676',
        linkTitle: "Je n'ai pas reçu le lien de confirmation",
      },
    ]}
    type="attention"
    className={styles['banner-email-adress']}
  >
    Pour valider ce changement, un lien de confirmation valable 24 heures vous a
    été envoyé à l’adresse :
    <span className={styles['banner-email-adress-email']}> {email}</span>
  </Banner>
)

export default BannerPendingEmailValidation

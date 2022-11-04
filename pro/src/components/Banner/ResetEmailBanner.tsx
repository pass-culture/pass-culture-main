import React from 'react'

import { Banner } from 'ui-kit'

// react hooks and usages doc : https://reactjs.org/docs/hooks-intro.html
import styles from './ResetEmailBanner.module.scss'

interface IResetEmailBannerProps {
  email: string
}

const ResetEmailBanner = ({ email }: IResetEmailBannerProps): JSX.Element => {
  return (
    <Banner
      links={[
        {
          href: 'https://aide.passculture.app/hc/fr/articles/4458607720732--Acteurs-Culturels-Comment-assurer-la-s%C3%A9curit%C3%A9-de-votre-compte-',
          linkTitle: "Je n'ai pas recu l'email",
        },
      ]}
    >
      Un e-mail a été envoyé à l’adresse :{' '}
      <span className={styles['reset-email-banner-email']}>{email}</span>.
      <br />
      Vous avez 24 heures pour activer votre changement d’adresse. Passé ce
      délai, votre changement d’e-mail ne sera pas pris en compte.
    </Banner>
  )
}

export default ResetEmailBanner

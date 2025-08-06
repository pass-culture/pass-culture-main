import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'

import styles from './BannerPendingEmailValidation.module.scss'

interface Props {
  email: string
}

export const BannerPendingEmailValidation = ({ email }: Props): JSX.Element => (
  <Callout
    links={[
      {
        href: 'https://aide.passculture.app/hc/fr/articles/5723750427676',
        label: 'Je n’ai pas reçu le lien de confirmation',
        isExternal: true,
      },
    ]}
    variant={CalloutVariant.ERROR}
    className={styles['banner-email-adress']}
  >
    Pour valider ce changement, un lien de confirmation valable 24 heures vous a
    été envoyé à l’adresse :
    <span className={styles['banner-email-adress-email']}> {email}</span>
  </Callout>
)

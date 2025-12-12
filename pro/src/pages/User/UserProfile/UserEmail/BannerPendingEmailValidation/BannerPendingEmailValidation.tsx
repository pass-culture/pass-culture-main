import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'

import styles from './BannerPendingEmailValidation.module.scss'

interface Props {
  email: string
}

export const BannerPendingEmailValidation = ({ email }: Props): JSX.Element => (
  <div className={styles['banner-email-adress']}>
    <Banner
      title="Confirmation requise"
      actions={[
        {
          href: 'https://aide.passculture.app/hc/fr/articles/5723750427676',
          label: 'Je n’ai pas reçu le lien de confirmation',
          isExternal: true,
          type: 'link',
          icon: fullLinkIcon,
          iconAlt: 'Nouvelle fenêtre',
        },
      ]}
      variant={BannerVariants.ERROR}
      description={
        <>
          Un lien de confirmation valable 24h a été envoyé à l’adresse :
          <span className={styles['banner-email-adress-email']}> {email}</span>
        </>
      }
    />
  </div>
)

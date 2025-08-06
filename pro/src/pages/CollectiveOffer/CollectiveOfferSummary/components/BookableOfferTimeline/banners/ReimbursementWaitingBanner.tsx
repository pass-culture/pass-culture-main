import fullEditIcon from 'icons/full-edit.svg'
import fullNextIcon from 'icons/full-next.svg'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'

import styles from '../BookableOfferTimeline.module.scss'

const config = {
  hasValidBankAccount: {
    message:
      'Les remboursements sont effectués toutes les 2 à 3 semaines. Vous serez notifié par mail une fois que le remboursement aura été versé.',
    link: {
      label: 'Comment fonctionne les remboursements ?',
      href: 'https://aide.passculture.app/hc/fr/articles/4411992051601--Acteurs-Culturels-Quand-votre-prochain-remboursement-sera-t-il-effectu%C3%A9',
      isExternal: true,
    },
  },
  hasPendingBankAccount: {
    message:
      'Vos coordonnées bancaires sont en cours de vérification par nos équipes.',
    link: {
      label: 'Suivre la validation de vos coordonnées bancaires',
      href: '/remboursements/informations-bancaires',
      icon: {
        src: fullNextIcon,
        alt: 'Consulter la validation des coordonnées bancaires',
      },
    },
  },
  hasNoBankAccount: {
    message: 'Ajoutez un compte bancaire pour débloquer le remboursement.',
    link: {
      label: 'Ajouter un compte bancaire',
      href: '/remboursements/informations-bancaires',
      icon: {
        src: fullEditIcon,
        alt: 'Ajouter un compte bancaire',
      },
    },
  },
}

const getBannerConfig = (
  hasValidBankAccount?: boolean,
  hasPendingBankAccount?: boolean
) => {
  if (hasValidBankAccount) {
    return config['hasValidBankAccount']
  }
  if (hasPendingBankAccount) {
    return config['hasPendingBankAccount']
  }
  return config['hasNoBankAccount']
}

export const ReimbursementWaitingBanner = ({
  hasValidBankAccount,
  hasPendingBankAccount,
}: {
  hasValidBankAccount?: boolean
  hasPendingBankAccount?: boolean
}) => {
  const { message, link } = getBannerConfig(
    hasValidBankAccount,
    hasPendingBankAccount
  )

  return (
    <Callout
      className={styles['callout']}
      variant={CalloutVariant.INFO}
      links={[link]}
    >
      {message}
    </Callout>
  )
}

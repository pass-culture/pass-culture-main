import { useMemo } from 'react'

import fullEditIcon from 'icons/full-edit.svg'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { Link } from 'ui-kit/LinkNodes/LinkNodes'

import styles from '../BookableOfferTimeline.module.scss'

type EndBannerProps = {
  offerId: number
  variant: 'lessThan48h' | 'moreThan48h' | 'moreThan48hWithoutBankInformation'
}

const editIcon = {
  src: fullEditIcon,
  alt: "Editer l'offre",
}

const configPerVariant = {
  lessThan48h: {
    message:
      'Nous espérons que votre évènement s’est bien déroulé. Si besoin, vous pouvez annuler la réservation ou modifier à la baisse le prix ou le nombre de participants jusqu’à 48 heures après la date de l’évènement.',
    link: {
      label: "Modifier à la baisse le prix ou le nombre d'élèves",
      href: '/offre/{offerId}/collectif/stocks/edition',
      icon: editIcon,
    },
  },
  moreThan48h: {
    message: 'Les remboursements sont effectués toutes les 2 à 3 semaines. Vous serez notifié par mail une fois que le remboursement aura été versé.',
    link: {
      label: 'Comment fonctionne les remboursements ?',
      href: 'https://aide.passculture.app/hc/fr/articles/4411992051601--Acteurs-Culturels-Quand-votre-prochain-remboursement-sera-t-il-effectu%C3%A9',
      isExternal: true,
    },
  },
  moreThan48hWithoutBankInformation: {
    message: 'Ajoutez un compte bancaire pour débloquer le remboursement.',
    link: {
      label: 'Ajouter un compte bancaire',
      href: '/remboursements/informations-bancaires',
      icon: editIcon,
    },
  },
} satisfies Record<
  EndBannerProps['variant'],
  {
    message: string
    link: Link
  }
>

export const EndBanner = ({ offerId, variant }: EndBannerProps) => {
  const { message, link: linkConfig } = useMemo(() => {
    return configPerVariant[variant]
  }, [variant])
  const href = linkConfig.href.replace('{offerId}', offerId.toString())
  const link = {
    ...linkConfig,
    href,
  }

  return (
    <Callout
      className={styles['callout']}
      variant={CalloutVariant.INFO}
      links={[
        link
      ]}
    >
      {message}
    </Callout>
  )
}

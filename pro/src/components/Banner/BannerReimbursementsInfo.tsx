import React from 'react'

import Callout from 'components/Callout/Callout'
import fullLinkIcon from 'icons/full-link.svg'

const BannerReimbursementsInfo = (): JSX.Element => {
  return (
    <Callout
      className="banner"
      links={[
        {
          href: 'https://passculture.zendesk.com/hc/fr/articles/4411992051601',
          linkTitle: 'Quand votre prochain remboursement sera-t-il effectué ?',
          icon: fullLinkIcon,
          svgAlt: 'Nouvelle fenêtre',
        },
        {
          href: 'https://passculture.zendesk.com/hc/fr/articles/4412007300369',
          linkTitle: 'Connaître les modalités de remboursement',
          icon: fullLinkIcon,
          svgAlt: 'Nouvelle fenêtre',
        },
      ]}
    >
      <p>
        Les remboursements s’effectuent tous les 15 jours, rétroactivement suite
        à la validation d’une contremarque dans le guichet ou à la validation
        automatique des contremarques d’évènements. Cette page est
        automatiquement mise à jour à chaque remboursement.
      </p>
    </Callout>
  )
}

export default BannerReimbursementsInfo

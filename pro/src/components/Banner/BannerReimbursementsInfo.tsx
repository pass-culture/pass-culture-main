import React from 'react'

import { Banner } from 'ui-kit'

const BannerReimbursementsInfo = (): JSX.Element => {
  return (
    <Banner
      type="notification-info"
      className="banner"
      links={[
        {
          href: 'https://passculture.zendesk.com/hc/fr/articles/4411992051601',
          linkTitle: 'En savoir plus sur les prochains remboursements',
        },
        {
          href: 'https://passculture.zendesk.com/hc/fr/articles/4412007300369',
          linkTitle: 'Connaître les modalités de remboursement',
        },
      ]}
    >
      <p>
        Les remboursements s’effectuent tous les 15 jours, rétroactivement suite
        à la validation d’une contremarque dans le guichet ou à la validation
        automatique des contremarques d’évènements. Cette page est
        automatiquement mise à jour à chaque remboursement.
      </p>
    </Banner>
  )
}

export default BannerReimbursementsInfo

import React from 'react'

import { Banner } from 'ui-kit'

const OfferRefundWarning = () => {
  return (
    <Banner
      links={[
        {
          href: 'https://aide.passculture.app/hc/fr/articles/6043184068252',
          linkTitle:
            'Quelles sont les offres numériques éligibles au remboursement ?',
          'aria-label': 'Nouvelle fenêtre',
        },
      ]}
      type="attention"
    >
      Cette offre numérique ne sera pas remboursée.
    </Banner>
  )
}

export default OfferRefundWarning

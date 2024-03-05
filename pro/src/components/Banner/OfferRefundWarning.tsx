import React from 'react'

import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'

const OfferRefundWarning = () => {
  return (
    <Callout
      links={[
        {
          href: 'https://aide.passculture.app/hc/fr/articles/6043184068252',
          isExternal: true,
          label:
            'Quelles sont les offres numériques éligibles au remboursement ?',
        },
      ]}
      variant={CalloutVariant.WARNING}
    >
      Cette offre numérique ne sera pas remboursée.
    </Callout>
  )
}

export default OfferRefundWarning

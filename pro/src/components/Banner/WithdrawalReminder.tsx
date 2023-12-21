import React from 'react'

import { Banner } from 'ui-kit'
import { CGU_URL } from 'utils/config'

const WithdrawalReminder = () => {
  return (
    <Banner
      links={[
        {
          href: CGU_URL,
          linkTitle: "Consulter les Conditions Générales d'Utilisation",
          'aria-label': 'Nouvelle fenêtre',
        },
      ]}
      type="notification-info"
    >
      La livraison d’article est interdite. Pour plus d’informations, veuillez
      consulter nos CGU.
    </Banner>
  )
}

export default WithdrawalReminder

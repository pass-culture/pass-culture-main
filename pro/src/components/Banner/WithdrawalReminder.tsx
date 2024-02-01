import React from 'react'

import { Banner } from 'ui-kit'
import { CGU_URL } from 'utils/config'

const WithdrawalReminder = () => {
  return (
    <Banner
      links={[
        {
          href: CGU_URL,
          label: "Consulter les Conditions Générales d'Utilisation",
          isExternal: true,
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

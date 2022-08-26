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
        },
      ]}
      type="notification-info"
    >
      La livraison d’article n’est pas autorisée. Pour plus d’informations,
      veuillez consulter nos CGU.
    </Banner>
  )
}

export default WithdrawalReminder

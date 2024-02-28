import React from 'react'

import Callout from 'components/Callout/Callout'
import { CGU_URL } from 'utils/config'

const WithdrawalReminder = () => {
  return (
    <Callout
      links={[
        {
          href: CGU_URL,
          label: "Consulter les Conditions Générales d'Utilisation",
          isExternal: true,
        },
      ]}
    >
      La livraison d’article est interdite. Pour plus d’informations, veuillez
      consulter nos CGU.
    </Callout>
  )
}

export default WithdrawalReminder

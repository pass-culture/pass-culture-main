import React from 'react'

import Banner from 'components/layout/Banner/Banner'
import { CGU_URL } from 'utils/config'

const WithdrawalReminder = () => {
  return (
    <Banner
      href={CGU_URL}
      linkTitle={"Consulter les Conditions Générales d'Utilisation"}
      message={
        "La livraison d'article n'est pas autorisée. Pour plus d'informations, veuillez consulter nos CGU."
      }
      type="notification-info"
    />
  )
}

export default WithdrawalReminder

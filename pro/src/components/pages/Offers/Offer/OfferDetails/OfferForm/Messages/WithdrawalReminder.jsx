/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import React from 'react'

import Banner from 'components/layout/Banner/Banner'
import { CGU_URL } from 'utils/config'

const WithdrawalReminder = () => {
  return (
    <Banner
      href={CGU_URL}
      linkTitle={"Consulter les Conditions Générales d'Utilisation"}
      type="notification-info"
    >
      La livraison d’article n’est pas autorisée. Pour plus d’informations, veuillez consulter nos
      CGU.
    </Banner>
  )
}

export default WithdrawalReminder

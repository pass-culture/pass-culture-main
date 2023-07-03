import React from 'react'

import strokeRepaymentIcon from 'icons/stroke-repayment.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

const InvoicesAdminMustFilter = (): JSX.Element => {
  return (
    <div className="no-refunds admin-view">
      <SvgIcon src={strokeRepaymentIcon} alt="" />
      <p className="admin-view-description">
        Pour visualiser vos justificatifs de remboursement, veuillez
        sélectionner un ou plusieurs des filtres précédents et cliquer sur
        «&nbsp;Lancer la recherche&nbsp;»
      </p>
    </div>
  )
}

export default InvoicesAdminMustFilter

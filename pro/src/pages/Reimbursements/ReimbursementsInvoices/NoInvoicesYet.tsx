import React from 'react'

import strokeRepaymentIcon from 'icons/stroke-repayment.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

const NoInvoicesYet = (): JSX.Element => {
  return (
    <div className="no-refunds admin-view">
      <SvgIcon src={strokeRepaymentIcon} alt="" />
      <p className="no-refunds-title">
        Vous n’avez pas encore de justificatifs de remboursement disponibles
      </p>
      <p className="no-refunds-description">
        Lorsqu’ils auront été édités, vous pourrez les télécharger ici
      </p>
    </div>
  )
}

export default NoInvoicesYet

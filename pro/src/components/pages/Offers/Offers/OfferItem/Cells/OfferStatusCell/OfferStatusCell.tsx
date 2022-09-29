import React from 'react'

import StatusLabel from 'components/pages/Offers/Offer/OfferStatus/StatusLabel'

const OfferStatusCell = ({ status }: { status: string }) => (
  <td className="status-column">
    <StatusLabel status={status} />
  </td>
)

export default OfferStatusCell

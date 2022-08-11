import React from 'react'

import Icon from 'components/layout/Icon'
import { Banner } from 'ui-kit'

const BannerReimbursementsInfo = (): JSX.Element => {
  return (
    <Banner type="notification-info" className="banner">
      En savoir plus sur
      <a
        className="bi-link tertiary-link"
        href="https://passculture.zendesk.com/hc/fr/articles/4411992051601"
        rel="noopener noreferrer"
        target="_blank"
      >
        <Icon svg="ico-external-site" className="banner-icon" />
        Les prochains remboursements
      </a>
      <a
        className="bi-link tertiary-link"
        href="https://passculture.zendesk.com/hc/fr/articles/4412007300369"
        rel="noopener noreferrer"
        target="_blank"
      >
        <Icon svg="ico-external-site" className="banner-icon" />
        Les modalités de remboursement
      </a>
    </Banner>
  )
}

export default BannerReimbursementsInfo

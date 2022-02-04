import React from 'react'

import { Banner } from 'ui-kit'

const StyleguideBanners = () => {
  const attentionBanner = String.raw`
    <Banner
      href="#"
      linkTitle="Lien vers une autre page"
    >
      {'Sous-titre du lien'}
    </Banner>
  `

  const informationBanner = String.raw`
    <Banner
      href="#"
      linkTitle="Lien vers une autre page"
      type="notification-info"
    >
      {"Bannière de type 'information'"}
    </Banner>
  `

  return (
    <div>
      <div className="flex-block">
        <Banner href="#" linkTitle="Lien vers une autre page">
          Bannière de type 'Attention'
        </Banner>
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>{attentionBanner}</code>
          </pre>
        </div>
      </div>
      <div className="flex-block">
        <Banner
          href="#"
          linkTitle="Lien vers une autre page"
          type="notification-info"
        >
          Bannière de type 'information'
        </Banner>
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>{informationBanner}</code>
          </pre>
        </div>
      </div>
      <br />
    </div>
  )
}

export default StyleguideBanners

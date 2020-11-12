import React from 'react'

import Banner from '../../../layout/Banner/Banner'

const StyleguideBanners = () => {
  const attentionBanner = String.raw`
    <Banner
      href="#"
      linkTitle="Lien vers une autre page"
      subtitle="Sous-titre du lien"
    />
  `

  const informationBanner = String.raw`
    <Banner
      href="#"
      linkTitle="Lien vers une autre page"
      subtitle="Bannière de type 'information'"
      type="notification-info"
    />
  `

  return (
    <div>
      <div className="flex-block">
        <Banner
          href="#"
          linkTitle="Lien vers une autre page"
          subtitle="Bannière de type 'Attention'"
        />
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>
              {attentionBanner}
            </code>
          </pre>
        </div>
      </div>
      <div className="flex-block">
        <Banner
          href="#"
          linkTitle="Lien vers une autre page"
          subtitle="Bannière de type 'information'"
          type="notification-info"
        />
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>
              {informationBanner}
            </code>
          </pre>
        </div>
      </div>
      <br />
    </div>
  )
}

export default StyleguideBanners

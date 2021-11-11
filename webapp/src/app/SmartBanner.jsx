import React from 'react'
import ReactSmartBanner from 'react-smartbanner'

const price = { ios: 'GRATUIT', android: 'GRATUIT' }
const storeText = { ios: "Sur l'App Store", android: 'Sur Google Play' }

const SmartBanner = () => (
  <ReactSmartBanner
    button="Voir"
    daysHidden={1}
    ignoreIosVersion
    position="top"
    price={price}
    storeText={storeText}
    title="pass Culture"
  />
)

export default SmartBanner

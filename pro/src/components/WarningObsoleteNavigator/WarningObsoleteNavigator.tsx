import { Banner, BannerVariants } from '@/design-system/Banner/Banner'

import supportedBrowsers from './supportedBrowsers.js'

export const WarningObsoleteNavigator = () => {
  const isObsoleteNavigator = () => {
    if (typeof navigator === 'undefined') {
      return false
    }

    return !supportedBrowsers.test(navigator.userAgent)
  }

  if (!isObsoleteNavigator()) {
    return null
  }

  return (
    <Banner
      variant={BannerVariants.WARNING}
      title="Votre navigateur est obsolète"
      description="Merci de mettre votre navigateur à jour pour une expérience optimale et sécurisée."
      actions={[
        {
          label: 'Liste des navigateurs compatibles',
          href: '/navigateurs-compatibles',
          isExternal: false,
          type: 'link',
        },
      ]}
    />
  )
}

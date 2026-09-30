import { useId } from 'react'

import type { VersionComparison } from '@/apiClient/backendVersionCompatibility'
import { ErrorLayout } from '@/app/App/layouts/ErrorLayout/ErrorLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { Link } from '@/design-system/Link/Link'
import strokeErrorIcon from '@/icons/stroke-error.svg'

export const BackendVersionMismatch = ({
  type,
}: {
  type: VersionComparison
}) => {
  const reloadUrl = new URL(window.location.href)
  reloadUrl.searchParams.set('_reload', Date.now().toString())
  const reloadPath = `${reloadUrl.pathname}${reloadUrl.search}${reloadUrl.hash}`
  const errorReturnLinkId = useId()

  const layoutParams =
    type === 'higher'
      ? {
          title: 'Une mise à jour est disponible',
          paragraph:
            "L'espace partenaire a été mis à jour. Cliquez ci-dessous pour continuer.",
          buttonText: 'Mettre à jour',
        }
      : {
          title: 'Mise à jour en cours',
          paragraph: (
            <>
              Nos équipes techniques finalisent l'installation d'une nouvelle
              version.
              <br />
              L'accès à votre espace sera rétabli d'ici quelques minutes en
              rechargeant la page.
              <br />
              Merci pour votre patience.
            </>
          ),
          buttonText: 'Si le problème persiste, merci de contacter nos équipes',
        }

  return (
    <ErrorLayout
      mainHeading={layoutParams.title}
      paragraph={layoutParams.paragraph}
      errorIcon={strokeErrorIcon}
      cta={
        type === 'higher' ? (
          <Button
            as="router-link"
            id={errorReturnLinkId}
            variant={ButtonVariant.SECONDARY}
            to={reloadPath}
            onClick={(event) => {
              event.preventDefault()
              window.location.replace(reloadUrl.toString())
            }}
            label={layoutParams.buttonText}
          />
        ) : (
          <Link
            isExternalLink
            shouldOpenNewTab
            to="https://aide.passculture.app/hc/fr/articles/13155602579356--Acteurs-Culturels-Quelle-%C3%A9quipe-contacter-selon-votre-demande"
            label={layoutParams.buttonText}
          />
        )
      }
    />
  )
}

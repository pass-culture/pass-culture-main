import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { Banner } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'

export const AccessibilityCallout = () => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const isAccessibilityDefinedViaAccesLibre =
    !!selectedPartnerVenue.externalAccessibilityId

  const callout = isAccessibilityDefinedViaAccesLibre
    ? {
        label: 'Éditer sur acceslibre',
        href: `https://acceslibre.beta.gouv.fr/contrib/edit-infos/${selectedPartnerVenue.externalAccessibilityId}/`,
        content:
          "Ces modalités proviennent d'acceslibre.gouv.fr et peuvent être modifiées directement sur cette plateforme.",
        title: 'Données Acceslibre',
      }
    : {
        label: 'Aller sur acceslibre.beta.gouv.fr',
        href: 'https://acceslibre.beta.gouv.fr/',
        content:
          "Complétez les modalités d'accessibilité de votre établissement sur acceslibre.beta.gouv.fr, la plateforme collaborative de l'accessibilité.",
        title: "Renseignez l'accessibilité",
      }

  return (
    <Banner
      title={callout.title}
      actions={[
        {
          href: callout.href,
          label: callout.label,
          isExternal: true,
          icon: fullLinkIcon,
          iconAlt: 'Nouvelle fenêtre',
          type: 'link',
        },
      ]}
      description={callout.content}
    />
  )
}

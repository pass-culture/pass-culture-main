import type { GetVenueResponseModel } from '@/apiClient/v1'
import { Banner } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'

interface AccessibilityCalloutProps {
  externalAccessibilityId?: GetVenueResponseModel['externalAccessibilityId']
  className?: string
}

export const AccessibilityCallout = ({
  externalAccessibilityId,
  className,
}: AccessibilityCalloutProps) => {
  const isAccessibilityDefinedViaAccesLibre = !!externalAccessibilityId
  const callout = isAccessibilityDefinedViaAccesLibre
    ? {
        label: 'Éditer sur acceslibre',
        href: `https://acceslibre.beta.gouv.fr/contrib/edit-infos/${externalAccessibilityId}/`,
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
    <div data-testid="accessibility-callout" className={className}>
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
    </div>
  )
}

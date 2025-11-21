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
          'Les modalités ci-dessus sont issues de la plateforme acceslibre.gouv.fr. Vous pouvez les modifier directement depuis cette plateforme.',
      }
    : {
        label: 'Aller sur acceslibre.beta.gouv.fr',
        href: 'https://acceslibre.beta.gouv.fr/',
        content:
          'Renseignez facilement les modalités d’accessibilité de votre établissement sur la plateforme collaborative acceslibre.beta.gouv.fr',
      }

  return (
    <div data-testid="accessibility-callout" className={className}>
      <Banner
        title=""
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

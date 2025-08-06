import { GetVenueResponseModel } from '@/apiClient/v1'
import { Callout } from '@/ui-kit/Callout/Callout'

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
    <Callout
      testId="accessibility-callout"
      className={className}
      links={[
        {
          href: callout.href,
          label: callout.label,
          isExternal: true,
        },
      ]}
    >
      {callout.content}
    </Callout>
  )
}

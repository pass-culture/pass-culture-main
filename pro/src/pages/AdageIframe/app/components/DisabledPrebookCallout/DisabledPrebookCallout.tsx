import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'

export const DisabledPrebookCallout = ({
  className,
}: {
  className: string
}) => {
  return (
    <Callout
      className={className}
      variant={CalloutVariant.WARNING}
      title={
        'Les préréservations des offres pass Culture sont temporairement suspendues.'
      }
    >
      Cette situation ne concerne que les établissements publics et privés du
      second degré du Ministère de l’Éducation nationale. Les établissements
      sous tutelle du ministère de l’Agriculture et de la Souveraineté
      Alimentaire, du ministère des Armées et du Secrétariat d’État à la Mer ne
      sont pas concernés.
    </Callout>
  )
}

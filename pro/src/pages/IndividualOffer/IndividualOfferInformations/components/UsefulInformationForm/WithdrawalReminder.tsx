import { CGU_URL } from 'commons/utils/config'
import { Callout } from 'ui-kit/Callout/Callout'

export const WithdrawalReminder = () => {
  return (
    <Callout
      links={[
        {
          href: CGU_URL,
          label: "Consulter les Conditions Générales d'Utilisation",
          isExternal: true,
        },
      ]}
    >
      La livraison d’article est interdite. Pour plus d’informations, veuillez
      consulter nos CGU.
    </Callout>
  )
}

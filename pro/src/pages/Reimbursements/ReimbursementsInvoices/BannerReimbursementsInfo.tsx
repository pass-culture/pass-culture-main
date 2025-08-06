import { Callout } from '@/ui-kit/Callout/Callout'

export const BannerReimbursementsInfo = (): JSX.Element => {
  return (
    <Callout
      title="Les remboursements s'effectuent toutes les 2 à 3 semaines"
      className="banner"
      links={[
        {
          href: 'https://passculture.zendesk.com/hc/fr/articles/4411992051601',
          label: 'En savoir plus sur les prochains remboursements',
          isExternal: true,
        },
        {
          href: 'https://passculture.zendesk.com/hc/fr/articles/4412007300369',
          label: 'Connaître les modalités de remboursement',
          isExternal: true,
        },
      ]}
    >
      <p>
        Nous remboursons en un virement toutes les réservations validées entre
        le 1ᵉʳ et le 15 du mois, et lors d’un second toutes celles validées
        entre le 16 et le 31 du mois.
      </p>
      <p>
        Les offres de type événement se valident automatiquement 48h à 72h après
        leur date de réalisation, leurs remboursements peuvent se faire sur la
        quinzaine suivante.
      </p>
    </Callout>
  )
}

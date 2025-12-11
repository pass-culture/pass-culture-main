import { Banner } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'

export const BannerReimbursementsInfo = (): JSX.Element => {
  return (
    <div className="banner">
      <Banner
        title="Les remboursements s'effectuent toutes les 2 à 3 semaines"
        actions={[
          {
            href: 'https://passculture.zendesk.com/hc/fr/articles/4411992051601',
            label: 'En savoir plus sur les prochains remboursements',
            isExternal: true,
            icon: fullLinkIcon,
            iconAlt: 'Nouvelle fenêtre',
            type: 'link',
          },
          {
            href: 'https://passculture.zendesk.com/hc/fr/articles/4412007300369',
            label: 'Connaître les modalités de remboursement',
            isExternal: true,
            icon: fullLinkIcon,
            iconAlt: 'Nouvelle fenêtre',
            type: 'link',
          },
        ]}
        description={
          <>
            <p>
              Nous remboursons en un virement toutes les réservations validées
              entre le 1ᵉʳ et le 15 du mois, et lors d’un second toutes celles
              validées entre le 16 et le 31 du mois.
            </p>
            <p>
              Les offres de type événement se valident automatiquement 48h à 72h
              après leur date de réalisation, leurs remboursements peuvent se
              faire sur la quinzaine suivante.
            </p>
          </>
        }
      />
    </div>
  )
}

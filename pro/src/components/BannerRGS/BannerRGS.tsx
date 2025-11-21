import { Banner } from '@/design-system/Banner/Banner'

interface Props {
  closable?: boolean
  onClose?: () => void
  className?: string
}

export const BannerRGS: React.FC<Props> = ({
  closable,
  onClose,
  className,
}: Props) => (
  <div className={className}>
    <Banner
      closable={closable}
      onClose={onClose}
      actions={[
        {
          href: 'https://aide.passculture.app/hc/fr/articles/4458607720732--Acteurs-Culturels-Comment-assurer-la-s%C3%A9curit%C3%A9-de-votre-compte-',
          label: 'Consulter nos recommandations de sécurité',
          isExternal: true,
          type: 'link',
        },
      ]}
      title="Soyez vigilant !"
      description="Vos identifiants de connexion sont personnels et ne doivent pas être
    partagés. Pour assurer la protection de votre compte, découvrez nos
    recommandations."
    />
  </div>
)

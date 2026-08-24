import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullDownloadIcon from '@/icons/full-download.svg'

import styles from './ActivationCodeFormDialog.module.scss'

interface AddActivationCodeFormProps {
  errorMessage: string
  errorTitle: string
}

export const AddActivationCodeForm = ({
  errorMessage,
  errorTitle,
}: AddActivationCodeFormProps) => {
  return (
    <>
      {errorMessage && (
        <div className={styles['activation-codes-errors']}>
          <Banner
            variant={BannerVariants.ERROR}
            title={errorTitle}
            description={errorMessage}
          />
        </div>
      )}

      <div className={styles['activation-codes-upload-banner']}>
        <Banner
          title="Vous ne possédez pas de fichier .csv ?"
          description="Afin de vous aider, vous pouvez télécharger un gabarit ci-dessous et y intégrer les codes d’activation correspondants à votre offre."
          actions={[
            {
              type: 'link',
              href: '/csvtemplates/CodesActivations-Gabarit.csv',
              isExternal: true,
              label: 'Télécharger le gabarit (.csv, 50ko)',
              icon: fullDownloadIcon,
              iconAlt: '',
            },
          ]}
        />
      </div>
    </>
  )
}

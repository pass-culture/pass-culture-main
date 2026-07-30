import { FormLayout } from '@/components/FormLayout/FormLayout'
import { PublicationAndBookingFields } from '@/components/PublicationAndBookingFields/PublicationAndBookingFields'
import { Divider } from '@/ui-kit/Divider/Divider'
import { TipsBanner } from '@/ui-kit/TipsBanner/TipsBanner'

import styles from './OfferPublicationForm.module.scss'

export const OfferPublicationForm = ({ maxDate }: { maxDate: string }) => {
  const sectionTitle = (
    <div className={styles['title-container']}>
      <span className={styles['title']}>Publication et réservation</span>
    </div>
  )

  return (
    <>
      <FormLayout fullWidthActions className={styles['form']}>
        <FormLayout.Section title={sectionTitle}>
          <FormLayout.MandatoryInfo />
          <FormLayout.Row
            sideComponent={
              <TipsBanner>
                Dans le cas où votre offre est en instruction par l’équipe
                Conformité, sa validation peut prendre jusqu’à 72h. <br />
                Après validation elle sera automatiquement publiée ou programmée
                comme vous l’avez choisi.
              </TipsBanner>
            }
          >
            <PublicationAndBookingFields maxDate={maxDate} />
          </FormLayout.Row>
        </FormLayout.Section>
      </FormLayout>
      <Divider />
    </>
  )
}

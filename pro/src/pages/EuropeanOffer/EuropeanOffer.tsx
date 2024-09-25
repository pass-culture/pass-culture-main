import { AppLayout } from 'app/AppLayout'
import { EuropeanOffer as EuropeanComponent } from 'components/EuropeanOffer/EuropeanOffer'

const EuropeanOffer = (): JSX.Element | null => {
  return (
    <AppLayout layout={'sticky-actions'}>
      <EuropeanComponent />
    </AppLayout>
  )
}

// Below exports are used by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = EuropeanOffer

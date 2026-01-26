import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import './NewHomepage.module.scss'

import { useAppSelector } from '@/commons/hooks/useAppSelector'

export const NewHomepage = (): JSX.Element => {
  const selectedVenue = useAppSelector((state) => state.user.selectedVenue)

  return (
    <BasicLayout mainHeading={`Votre espace ${selectedVenue?.publicName}`}>
      <p>Hello world</p>
    </BasicLayout>
  )
}

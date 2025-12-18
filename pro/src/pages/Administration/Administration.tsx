import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'

export const Administration = () => {
  return (
    <BasicLayout mainHeading="Administration" backTo={{ to: '/accueil' }}>
      <div>test</div>
    </BasicLayout>
  )
}

export const Component = Administration

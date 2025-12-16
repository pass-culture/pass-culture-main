import type { StoryObj } from '@storybook/react-vite'
import { withRouter } from 'storybook-addon-remix-react-router'

import { ShareLink } from './ShareLink'
import { configureTestStore } from '@/commons/store/testUtils'
import { Provider } from 'react-redux'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

export default {
  title: '@/ui-kit/ShareLink',
  decorators: [withRouter],
  component: ShareLink,
}

export const Default: StoryObj<typeof ShareLink> = {
  render: (args) => (
    <Provider store={configureTestStore({})}>
      <div style={{ width: '100%' }}>
        <ShareLink {...args} />
      </div>
      <SnackBarContainer />
    </Provider>
  ),
  args: {
    link: 'https://bv.ac-versailles.fr/adage/passculture/offres/offerid/8 ',
    label: 'Lien de l’offre',
    notifySuccessMessage: 'Le lien ADAGE a bien été copié',
  },
}

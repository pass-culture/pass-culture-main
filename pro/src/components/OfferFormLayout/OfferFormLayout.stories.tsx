import React from 'react'
import { withRouter } from 'storybook-addon-react-router-v6'

import { OfferIndividualBreadcrumb } from 'components/OfferIndividualBreadcrumb'

import { OfferFormLayout } from '.'

export default {
  title: 'components/OfferFormLayout',
  component: OfferFormLayout,
  decorators: [withRouter],
}

const Actions = () => (
  <div>
    <button>Clique-moi</button>
    <span>Statut</span>
  </div>
)

const Template = () => (
  <div style={{ width: 780 }}>
    <OfferFormLayout>
      <OfferFormLayout.TitleBlock actions={Actions()}>
        <h1>"Mon super titre !</h1>
        <h4>Le nom de mon offre</h4>
      </OfferFormLayout.TitleBlock>

      <OfferFormLayout.Stepper>
        <OfferIndividualBreadcrumb />
      </OfferFormLayout.Stepper>

      <OfferFormLayout.Content>
        <div>
          <h5>Info</h5>
          <p>
            Lorem Ipsum is simply dummy text of the printing and typesetting
            industry. Lorem Ipsum has been the industry's standard dummy text
            ever since the 1500s, when an unknown printer took a galley of type
            and scrambled it to make a type specimen book. It has survived not
            only five centuries, but also the leap into electronic typesetting,
            remaining essentially unchanged. It was popularised in the 1960s
            with the release of Letraset sheets containing Lorem Ipsum passages,
            and more recently with desktop publishing software like Aldus
            PageMaker including versions of Lorem Ipsum.
          </p>
        </div>
      </OfferFormLayout.Content>
    </OfferFormLayout>
  </div>
)

export const Default = Template.bind({})

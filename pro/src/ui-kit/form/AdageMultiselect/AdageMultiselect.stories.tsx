import type { Story } from '@storybook/react'
import { Formik } from 'formik'
import React from 'react'

import AdageMultiselect from './AdageMultiselect'

export default {
  title: 'ui-kit/forms/AdageMultiselect',
  component: AdageMultiselect,
}

const options = [
  { key: '1', value: 'Architecture' },
  { key: '2', value: 'Arts du cirque et arts de la rue' },
  { key: '3', value: 'Gastronomie et arts du goût' },
  { key: '4', value: 'Arts numériques' },
  { key: '5', value: 'Arts visuels, arts plastiques, arts appliqués' },
  { key: '6', value: 'Cinéma, audiovisuel' },
  { key: '7', value: 'Culture scientifique, technique et industrielle' },
  { key: '8', value: 'Danse' },
  { key: '9', value: 'Design' },
  { key: '10', value: 'Développement durable' },
  { key: '11', value: 'Univers du livre, de la lecture et des écritures' },
  { key: '12', value: 'Musique' },
  { key: '13', value: 'Patrimoine, mémoire, archéologie' },
  { key: '14', value: 'Photographie' },
  { key: '15', value: 'Théâtre, expression dramatique, marionnettes' },
  { key: '16', value: 'Bande dessinée' },
  { key: '17', value: 'Média et information' },
]

const Template: Story = () => (
  <Formik initialValues={{ educationalDomains: [] }} onSubmit={() => {}}>
    <AdageMultiselect
      options={options}
      placeholder="Ex: Théâtre"
      name="educationalDomains"
      label="Rechercher un domaine artistique"
    />
  </Formik>
)

export const Default = Template.bind({})

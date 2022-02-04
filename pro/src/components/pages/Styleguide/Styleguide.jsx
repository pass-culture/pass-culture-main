import React from 'react'

import AppLayout from 'app/AppLayout'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'

import StyleguideAgenda from './StyleguideAgenda'
import StyleguideBanners from './StyleguideElements/StyleguideBanners'
import StyleguideButtons from './StyleguideElements/StyleguideButtons'
import StyleguideCheckboxes from './StyleguideElements/StyleguideCheckboxes'
import StyleguideInputDuration from './StyleguideElements/StyleguideInputDuration'
import StyleguideInputText from './StyleguideElements/StyleguideInputText'
import StyleguideInputTextarea from './StyleguideElements/StyleguideInputTextarea'
import StyleguideSelect from './StyleguideElements/StyleguideSelect'
import StyleguideTitles from './StyleguideElements/StyleguideTitles'
import StyleguideTitle from './StyleguideTitles'

const Styleguide = () => (
  <AppLayout layoutConfig={{ pageName: 'styleguide' }}>
    <PageTitle title="Guide des styles" />
    <Titles title="Styleguide" />
    <StyleguideAgenda />

    <StyleguideTitle className="sg-titles" componentName="Titres" />
    <StyleguideTitles />

    <StyleguideTitle className="sg-buttons" componentName="Boutons" />
    <StyleguideButtons />

    <StyleguideTitle className="sg-inputtext" componentName="Inputs" />
    <StyleguideInputText />

    <StyleguideTitle className="sg-inputtime" componentName="InputDuration" />
    <StyleguideInputDuration />

    <StyleguideTitle className="sg-textarea" componentName="Textarea" />
    <StyleguideInputTextarea />

    <StyleguideTitle className="sg-select" componentName="Select" />
    <StyleguideSelect />

    <StyleguideTitle className="sg-checkbox" componentName="InputCheckbox" />
    <StyleguideCheckboxes />

    <StyleguideTitle className="sg-banner" componentName="Bannière" />
    <StyleguideBanners />
  </AppLayout>
)

export default Styleguide

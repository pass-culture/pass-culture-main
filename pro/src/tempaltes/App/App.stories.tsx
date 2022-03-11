import React from 'react'

import Header from 'components/layout/Header'
import { App } from '.'

export default {
  title: 'templates/App',
  component: App,
}

const ContentTemplate = () => (
  <App>
    <App.Header>
      {/* <div>Header !</div> */}
      <Header />
    </App.Header>
    <App.ContentCenter>
      <span>hello centered content !</span>
    </App.ContentCenter>
  </App>
)

export const Content = ContentTemplate.bind({})

const FullScreenTempalte = () => (
  <App>
    <App.Header>
      <div>Header !</div>
    </App.Header>
    <App.FullScreen>
      <div>hello full screen content !</div>
    </App.FullScreen>
  </App>
)

export const FullScreen = FullScreenTempalte.bind({})

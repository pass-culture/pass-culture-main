import React from 'react'

import Header from 'components/layout/Header'
import { PageCenter, PageFullScreen } from 'templates/Page'
import { App } from '.'

export default {
  title: 'templates/App',
  component: App,
}

const PageCenterTemplate = () => (
  <App>
    <App.Header>
      <Header />
    </App.Header>
    <App.Content>
      <PageFullScreen>
        <div>Here a centered page</div>
      </PageFullScreen>
    </App.Content>
  </App>
)

export const Content = PageCenterTemplate.bind({})

const PageFullScreenTemplate = () => (
  <App>
    <App.Header>
      <div>Header !</div>
    </App.Header>
    <App.Content>
      <PageFullScreen>
        <div>hello full screen content !</div>
      </PageFullScreen>
    </App.Content>
  </App>
)

export const FullScreen = PageFullScreenTemplate.bind({})

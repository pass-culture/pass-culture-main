const DisableTryItOutPlugin = () => ({
  statePlugins: {
    spec: {
      wrapSelectors: {
        allowTryItOutFor: () => () => false
      }
    }
  }
})

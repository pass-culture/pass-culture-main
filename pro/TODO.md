# TODO

- [ ] essayer sur une occurence:
  - [x] ajouter un router dans les tests de useNotification
  - [x] spliter les tests
  - [ ] vérifier que ça marche toujours quand aucune url est définie
  - [ ] stocker l'url avec la notif au moment du dispatch showNotification
  - [ ] si l'url est définie, conditionner l'affichage de la notif au fait de se trouver sur la bonne page
- [ ] ajouter l'url sur laquelle la notif doit s'afficher sur toutes les occurrences

[MobTime](https://mobtime.onrender.com/mob/pass-culture)

```ts
const TestSuccess = (): JSX.Element => {
  const notify = useNotification()

  notify.success('notfication sucess', {
    duration: 1,
  })
  notify.close()

  return <></>
}
const TestError = (): JSX.Element => {
  const notify = useNotification()
  notify.error('notification error', {
    duration: 3,
  })
  return <></>
}
const TestInformation = (): JSX.Element => {
  const notify = useNotification()
  notify.information('notification information', {
    duration: 2,
  })
  return <></>
}
const TestPending = (): JSX.Element => {
  const notify = useNotification()
  notify.pending('notification pending', {
    duration: 2,
  })
  return <></>
}

const renderAppTest = (initialPage: string) => {
  render(
    <Provider store={configureTestStore()}>
      <MemoryRouter initialEntries={[initialPage]}>
        <Route path="/page1">
          <h1>Page 1</h1>
        </Route>
        <Route path="/success">
          <TestSuccess />
        </Route>
        <Route path="/error">
          <TestError />
        </Route>
        <Route path="/information">
          <TestInformation />
        </Route>
        <Route path="/pending">
          <TestPending />
        </Route>
      </MemoryRouter>
    </Provider>
  )
}
```

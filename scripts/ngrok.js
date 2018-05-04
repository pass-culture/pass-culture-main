const fetch = require('node-fetch')
fetch('http://localhost:4040')
  .then(r => r.text())
  .then(t => {
    const jsonString = JSON.parse(t.match(/JSON.parse(.*);/g)[1]
                        .split('JSON.parse(')[1]
                        .slice(0, -2))

    const json = JSON.parse(jsonString)
    console.log(json.Session.Tunnels.api.URL)
  })

const API_BASE_URL = 'http://localhost:5001'

async function save_sandbox() {
  console.log('before:run ~~~ ~~~ ~~~ ~~~ ~~~ end')
  try {
    await fetch(`${API_BASE_URL}/health/api`)
    console.log('health check success')
  } catch (error) {
    console.error(error)
    throw error
  }
  try {
    const current_jobs = await fetch(`${API_BASE_URL}/e2e/pro/is-up`).then(
      (res) => res.json()
    )
    console.log('current_jobs', current_jobs)
    await fetch(`${API_BASE_URL}/e2e/pro/tear-up`)
      .then((res) => res.status)
      .then(console.log)
    let is_up = false
    const loop_call = setInterval(async () => {
      await fetch(`${API_BASE_URL}/e2e/pro/is-up`).then((res) => {
        const response = res.json().then(console.log)
        console.log('is_up', response)
      })
    }, 1000)
    if (is_up) clearInterval(loop_call)
  } catch (error) {
    console.error(error)
    throw error
  }
}

save_sandbox()

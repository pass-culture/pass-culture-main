const s = require('inflection')

module.exports = {
  prompt: ({ inquirer }) => {
    const questions = [
      // TODO: we need to properly formalize atomic design
      // {
      //   type: 'select',
      //   name: 'category',
      //   message: 'Which Atomic design level?',
      //   choices: ['atoms', 'molecules', 'organisms', 'templates', 'pages'],
      // },
      {
        type: 'select',
        name: 'category',
        message: 'Which design level?',
        choices: [
          'ui-kit',
          'new_components',
          'screens',
          'templates',
          'pages',
          'routes',
        ],
      },
      {
        type: 'input',
        name: 'component_name',
        message: 'What is the component name?',
      },
      {
        type: 'input',
        name: 'dir',
        message: 'Where is the directory(Optional)',
      },
    ]
    return inquirer.prompt(questions).then(answers => {
      const { category, component_name, dir } = answers
      const path = `${category}/${dir ? `${dir}/` : ``}${component_name}`
      const absPath = `src/${path}`
      const storybookBaseUrl =
        'https://pass-culture.github.io/pass-culture-main'

      const includeScss = !['routes'].includes(category)
      const includeStorie = !['routes'].includes(category)
      const includeReadme = !['routes'].includes(category)

      const ComponentName = s.camelize(component_name)
      const cssClassName = ComponentName
      .replace( /([A-Z])/g, " $1" )
      .trim()
      .replace(/ /g, '-')
      .toLowerCase()
      const testId = `test-${cssClassName}`

      return {
        ...answers,
        path,
        absPath,
        category,
        storybookBaseUrl,
        includeScss,
        includeStorie,
        includeReadme,
        ComponentName,
        cssClassName,
        testId,
      }
    })
  },
}

export default {
  templateFolderName: 'component',

  filesToGenerate: [
    // 1st file will always be generated
    {
      templateFileName: '<% name %>.tsx.mustache',
    },
    // Yes/No questions …
    {
      templateFileName: '<% name %>.module.scss.mustache',
      question: 'Generate SCSS module?',
      varName: 'scss',
    },
    {
      templateFileName: '<% name %>.spec.tsx.mustache',
      question: 'Generate test file?',
      varName: 'spec',
    },
    {
      templateFileName: '<% name %>.stories.tsx.mustache',
      question: 'Generate storybook file?',
      varName: 'story',
    },
    {
      question: 'Will this component be lazy-loaded by react-router?',
      varName: 'lazy',
    },
  ],
}

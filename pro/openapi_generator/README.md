# OpenApi Generator

* [documention openApiGenerator](https://openapi-generator.tech/docs/)
* [github openApiGenerator](https://github.com/OpenAPITools/openapi-generator)
* [documentation typescript-fetch generator](https://openapi-generator.tech/docs/generators/typescript-fetch)
* [documentation pydantic](https://pydantic-docs.helpmanual.io/)

## Schema open api

### Sur testing (aka master)

* [pro](https://backend.passculture-testing.beta.gouv.fr/pro/openapi.json)
* [contremarque](https://backend.passculture-testing.beta.gouv.fr/v2/openapi.json)

### Sur votre environement local

* [pro ](https://backend.passculture-testing.beta.gouv.fr/pro/openapi.json)
* [contremarque](https://backend.passculture-testing.beta.gouv.fr/v2/openapi.json)

## Global configuration options

[see documentation](https://openapi-generator.tech/docs/globals)

## generate help

```shell
openapi-generator-cli help generate
NAME
  openapi-generator-cli generate - Generate code with the specified
  generator.
SYNOPSIS
  openapi-generator-cli generate
    [(-a <authorization> | --auth <authorization>)]
    [--api-name-suffix <api name suffix>] [--api-package <api package>]
    [--artifact-id <artifact id>] [--artifact-version <artifact version>]
    [(-c <configuration file> | --config <configuration file>)] [--dry-run]
    [(-e <templating engine> | --engine <templating engine>)]
    [--enable-post-process-file]
    [(-g <generator name> | --generator-name <generator name>)]
    [--generate-alias-as-model] [--git-host <git host>]
    [--git-repo-id <git repo id>] [--git-user-id <git user id>]
    [--global-property <global properties>...] [--group-id <group id>]
    [--http-user-agent <http user agent>]
    [(-i <spec file> | --input-spec <spec file>)]
    [--ignore-file-override <ignore file override location>]
    [--import-mappings <import mappings>...]
    [--instantiation-types <instantiation types>...]
    [--invoker-package <invoker package>]
    [--language-specific-primitives <language specific primitives>...]
    [--legacy-discriminator-behavior] [--library <library>]
    [--log-to-stderr] [--minimal-update]
    [--model-name-prefix <model name prefix>]
    [--model-name-suffix <model name suffix>]
    [--model-package <model package>]
    [(-o <output directory> | --output <output directory>)] [(-p <additional properties> | --additional-properties <additional properties>)...]
    [--package-name <package name>] [--release-note <release note>]
    [--remove-operation-id-prefix]
    [--reserved-words-mappings <reserved word mappings>...]
    [(-s | --skip-overwrite)] [--server-variables <server variables>...]
    [--skip-operation-example] [--skip-validate-spec]
    [--strict-spec <true/false strict behavior>]
    [(-t <template directory> | --template-dir <template directory>)]
    [--type-mappings <type mappings>...] [(-v | --verbose)]
```
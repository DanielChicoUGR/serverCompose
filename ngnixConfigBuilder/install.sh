#!/bin/env bash


set -x
uv build

uv tool install dist/nginxconfigbuilder-0.1.0-py3-none-any.whl

set +x
echo "✅ Instalación completada"

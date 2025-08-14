#!/bin/bash
# Script para rodar collectstatic e garantir que a pasta staticfiles seja copiada para static para o Vercel servir corretamente

python3 manage.py collectstatic --noinput

# Remove a pasta static antiga, se existir
rm -rf static

# Copia tudo de staticfiles para static
cp -r staticfiles static
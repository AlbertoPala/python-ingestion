#!/bin/bash
set -e

# Leer dependencias de los metadatos del cluster
# La llave se define en el generador Dataproc bajo 'metadata': {'pip-install': 'paquete1 paquete2'}
PIP_PACKAGES=$(/usr/share/google/get_metadata_value attributes/pip-install || echo "")

if [[ -n "${PIP_PACKAGES}" ]]; then
    echo "Instalando paquetes: ${PIP_PACKAGES}"
    pip install ${PIP_PACKAGES}
else
    echo "No se encontraron paquetes para instalar en la metadata 'pip-install'."
fi

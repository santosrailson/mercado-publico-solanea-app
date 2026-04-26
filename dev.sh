#!/bin/bash

# Script para facilitar o desenvolvimento

case "$1" in
  "dev")
    echo "Iniciando ambiente de desenvolvimento..."
    docker-compose up -d
    ;;
  "stop")
    echo "Parando containers..."
    docker-compose down
    ;;
  "logs")
    docker-compose logs -f
    ;;
  "build")
    echo "Reconstruindo containers..."
    docker-compose up -d --build
    ;;
  "reset")
    echo "Resetando banco de dados..."
    docker-compose down -v
    docker-compose up -d
    ;;
  "shell-backend")
    docker-compose exec backend /bin/sh
    ;;
  "shell-frontend")
    docker-compose exec frontend /bin/sh
    ;;
  *)
    echo "Uso: ./dev.sh [comando]"
    echo ""
    echo "Comandos:"
    echo "  dev           - Inicia ambiente de desenvolvimento"
    echo "  stop          - Para containers"
    echo "  logs          - Mostra logs"
    echo "  build         - Reconstrói containers"
    echo "  reset         - Reset banco de dados"
    echo "  shell-backend - Acessa shell do backend"
    echo "  shell-frontend- Acessa shell do frontend"
    ;;
esac
